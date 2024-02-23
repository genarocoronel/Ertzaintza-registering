import base64
import hashlib
import os, functools
import zeep_plugins, datetime
from lxml.etree import QName
import xmlsec#, xmlsec.constants
import lxml.etree as etree

from zeep import ns
from zeep.wsse import utils
from zeep.wsse.utils import WSU, get_security_header, get_timestamp
from zeep.wsse import BinarySignature, UsernameToken
from zeep.wsse.signature import BinarySignature
from zeep.wsse.utils import ensure_id, get_security_header, ID_ATTR
from zeep.utils import detect_soap_env

def format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def _make_sign_key(key_data, cert_data, password, key_format=2):
    # 2 is the key format for PEM
    key = xmlsec.Key.from_memory(key_data, key_format, password)
    key.load_cert_from_memory(cert_data, 2)
    return key




def _sign_node(ctx, signature, target, digest_method=None):
    """Add sig for ``target`` in ``signature`` node, using ``ctx`` context.

    Doesn't actually perform the signing; ``ctx.sign(signature)`` should be
    called later to do that.

    Adds a Reference node to the signature with URI attribute pointing to the
    target node, and registers the target node's ID so XMLSec will be able to
    find the target node by ID when it signs.

    """

    # Ensure the target node has a wsu:Id attribute and get its value.
    node_id = ensure_id(target)

    # Unlike HTML, XML doesn't have a single standardized Id. WSSE suggests the
    # use of the wsu:Id attribute for this purpose, but XMLSec doesn't
    # understand that natively. So for XMLSec to be able to find the referenced
    # node by id, we have to tell xmlsec about it using the register_id method.
    ctx.register_id(target, "Id", ns.WSU)

    # Add reference to signature with URI attribute pointing to that ID.
    uri = "#" + node_id
    sap = f'.//*[local-name()="Reference" and @URI="{uri}"]'
    sip = signature.xpath(sap)
    if len(sip) > 0:
        ref = sip[0]
        ref.getparent().remove(ref)
    if digest_method is False:
        ref = xmlsec.template.add_reference(
            signature, None, uri="#" + node_id
        )
    else:
        ref = xmlsec.template.add_reference(
            signature, digest_method or xmlsec.Transform.SHA1, uri="#" + node_id
        )
    # This is an XML normalization transform which will be performed on the
    # target node contents before signing. This ensures that changes to
    # irrelevant whitespace, attribute ordering, etc won't invalidate the
    # signature.
    xmlsec.template.add_transform(ref, xmlsec.Transform.EXCL_C14N)
    pass


class PersonalizedBinarySignature(BinarySignature):
    """Sign given SOAP envelope with WSSE sig using given key file and cert file.

    Place the key information into BinarySecurityElement."""

    def __init__(
        self,
        key_file,
        certfile,
        password=None,
        signature_method=None,
        digest_method=None,
        key_format=6 #6 is the key format for PCKS12 PEM
    ):
        self.key_format = key_format
        super().__init__(
            key_file, certfile, password=password, signature_method=signature_method,
            digest_method=digest_method,
        )
    def apply(self, envelope, headers):
        key = _make_sign_key(self.key_data, self.cert_data, self.password, self.key_format)
        key_manager = xmlsec.KeysManager()
        # 2 is the key format for PEM, and 256 means xmlsec.constants.KeyDataTypeTrusted
        key_manager.load_cert_from_memory(self.cert_data, 2, 256)
        self._sign_envelope_with_key_binary(
            envelope, key, self.signature_method, self.digest_method, key_manager
        )
        return envelope, headers

    def _sign_envelope_with_key_binary(self, envelope, key, signature_method, digest_method, key_manager):

        security, sec_token_ref, x509_data, bintok = self._signature_prepare(
            envelope, key, signature_method, digest_method, key_manager
        )
        bintok.text = base64.b64encode(self.cert_data).decode("utf-8")
        security.insert(1, bintok)
        x509_data.getparent().remove(x509_data)

    def _signature_prepare(self, envelope, key, signature_method, digest_method, key_manager):
        """Prepare envelope and sign."""
        soap_env = detect_soap_env(envelope)

        #Gets the wsse:Security header
        security = get_security_header(envelope)

        # Create the Signature node if it does not exist.
        signature = self.add_if_absent(security, xmlsec.template.create, QName(ns.DS, "Signature"),                 envelope,
                xmlsec.Transform.EXCL_C14N,
                signature_method or xmlsec.Transform.RSA_SHA1,
        )


        # Add a KeyInfo node with X509Data child to the Signature. XMLSec will fill
        # in this template with the actual certificate details when it signs.
        key_info = xmlsec.template.ensure_key_info(signature)
        x509_data = xmlsec.template.add_x509_data(key_info)
        xmlsec.template.x509_data_add_issuer_serial(x509_data)
        xmlsec.template.x509_data_add_certificate(x509_data)

        security = get_security_header(envelope)

        # Place the X509 data inside a WSSE SecurityTokenReference within
        # KeyInfo. The recipient expects this structure, but we can't rearrange
        # like this until after signing, because otherwise xmlsec won't populate
        # the X509 data (because it doesn't understand WSSE).
        sec_token_ref = etree.SubElement(key_info, QName(ns.WSSE, "SecurityTokenReference"))

        # Perform the actual signing.
        ctx = xmlsec.SignatureContext()
        ctx.key = key
        _sign_node(ctx, signature, envelope.find(QName(soap_env, "Body")), digest_method)
        timestamp = security.find(QName(ns.WSU, "Timestamp"))
        if timestamp != None:
            _sign_node(ctx, signature, timestamp, digest_method)

        bintok = self.add_if_absent(security, functools.partial(etree.Element, QName(ns.WSSE, "BinarySecurityToken")), QName(ns.WSSE, "BinarySecurityToken"),                {
                    "ValueType": "http://docs.oasis-open.org/wss/2004/01/"
                    "oasis-200401-wss-x509-token-profile-1.0#X509v3",
                    "EncodingType": "http://docs.oasis-open.org/wss/2004/01/"
                    "oasis-200401-wss-soap-message-security-1.0#Base64Binary",
                })

        srtok = self.add_if_absent(security, functools.partial(etree.SubElement, sec_token_ref, QName(ns.WSSE, "Reference")),
                QName(ns.WSSE, "Reference"),
                {
                    "ValueType": "http://docs.oasis-open.org/wss/2004/01/"
                    "oasis-200401-wss-x509-token-profile-1.0#X509v3"
                })


        srtok.attrib["URI"] = "#" + ensure_id(bintok)
        bintok.text = base64.b64encode(self.cert_data).decode("utf-8")

        _sign_node(ctx, signature, bintok, digest_method)
        ctx.sign(signature)

        #bintok.text = x509_data.find(QName(ns.DS, "X509Certificate")).text
        #certificates = x509_data.xpath('.//*[local-name()="X509Certificate"]')
        #x509certificate_node = x509_data.find(QName(ns.DS, "X509Certificate"))
        #x509certificate_node = etree.SubElement(x509_data, QName(ns.DS, "X509Certificate"))
        #ctx.sign_binary(self.cert_data, transform=xmlsec.Transform.RSA_SHA1)

        return security, sec_token_ref, x509_data, bintok

    def add_if_absent(self, parent, function, qname, *extra_args):
        #bst_qname = QName(ns.WSSE, "BinarySecurityToken")
        element = parent.find(qname)
        if element is None:
            element = function(*extra_args)
            parent.insert(0, element)#or 1 sometimes?
        return element


class TimestampToken:
    """UsernameToken Profile 1.1

    https://docs.oasis-open.org/wss/v1.1/wss-v1.1-spec-os-UsernameTokenProfile.pdf

    Example response using PasswordText::

        <wsse:Security>
          <wsse:UsernameToken>
            <wsse:Username>scott</wsse:Username>
            <wsse:Password Type="wsse:PasswordText">password</wsse:Password>
          </wsse:UsernameToken>
        </wsse:Security>

    Example using PasswordDigest::

        <wsse:Security>
          <wsse:UsernameToken>
            <wsse:Username>NNK</wsse:Username>
            <wsse:Password Type="wsse:PasswordDigest">
                weYI3nXd8LjMNVksCKFV8t3rgHh3Rw==
            </wsse:Password>
            <wsse:Nonce>WScqanjCEAC4mQoBE07sAQ==</wsse:Nonce>
            <wsu:Created>2003-07-16T01:24:32Z</wsu:Created>
          </wsse:UsernameToken>
        </wsse:Security>

    """

    username_token_profile_ns = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0"  # noqa
    soap_message_secutity_ns = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0"  # noqa

    def __init__(
        self,
        username=None,
        password=None,
        password_digest=None,
        use_digest=False,
        nonce=None,
        created=None,
        timestamp_token=None,
        zulu_timestamp=None,
        hash_password=None,
    ):
        """
        Some SOAP services want zulu timestamps with Z in timestamps and
        in password digests they may want password to be hashed before
        adding it to nonce and created.
        """
        self.username = username
        self.password = password
        self.password_digest = password_digest
        self.nonce = nonce
        self.created = created
        self.use_digest = use_digest
        self.timestamp_token = timestamp_token
        self.zulu_timestamp = zulu_timestamp
        self.hash_password = hash_password

    def apply(self, envelope, headers):
        security = utils.get_security_header(envelope)

        # The token placeholder might already exists since it is specified in
        # the WSDL.
        token = security.find("{%s}UsernameToken" % ns.WSSE)
        if token is None:
            token = utils.WSSE.UsernameToken()
            security.append(token)

        if self.timestamp_token is not None:
            security.append(self.timestamp_token)

        # Create the sub elements of the UsernameToken element
        if self.username is not None:
            elements = [utils.WSSE.Username(self.username)]
            if self.password is not None or self.password_digest is not None:
                if self.use_digest:
                    elements.extend(self._create_password_digest())
                else:
                    elements.extend(self._create_password_text())
            token.extend(elements)

        return envelope, headers

    def verify(self, envelope):
        pass

    def _create_password_text(self):
        return [
            utils.WSSE.Password(
                self.password, Type="%s#PasswordText" % self.username_token_profile_ns
            )
        ]

    def _create_password_digest(self):
        if self.nonce:
            nonce = self.nonce.encode("utf-8")
        else:
            nonce = os.urandom(16)
        timestamp = utils.get_timestamp(self.created, self.zulu_timestamp)

        if isinstance(self.password, str):
            password = self.password.encode("utf-8")
        else:
            password = self.password

        # digest = Base64 ( SHA-1 ( nonce + created + password ) )
        if not self.password_digest and self.hash_password:
            digest = base64.b64encode(
                hashlib.sha1(
                    nonce + timestamp.encode("utf-8") + hashlib.sha1(password).digest()
                ).digest()
            ).decode("ascii")
        elif not self.password_digest:
            digest = base64.b64encode(
                hashlib.sha1(nonce + timestamp.encode("utf-8") + password).digest()
            ).decode("ascii")
        else:
            digest = self.password_digest

        return [
            utils.WSSE.Password(
                digest, Type="%s#PasswordDigest" % self.username_token_profile_ns
            ),
            utils.WSSE.Nonce(
                base64.b64encode(nonce).decode("utf-8"),
                EncodingType="%s#Base64Binary" % self.soap_message_secutity_ns,
            ),
            utils.WSU.Created(timestamp),
        ]


def get_username_token(username, password, use_digest=False, ttl=60000):
    timestamp_token = WSU.Timestamp()
    #created = WSU.Created(format_datetime(datetime.datetime.now(datetime.UTC)))
    timestamp_token.attrib[QName(zeep_plugins.XMLNamespaces.wsu, 'Id')] = "idTimestampToken"
    today_datetime = datetime.datetime.today()
    expires_datetime = today_datetime + datetime.timedelta(seconds=ttl)
    timestamp_elements = [
        WSU.Created(format_datetime(today_datetime)),
        WSU.Expires(format_datetime(expires_datetime)),
        #WSU.Nonce(base64.b64encode(os.urandom(16)).decode('utf-8'))
    ]
    timestamp_token.extend(timestamp_elements)
    #user_name_token = TimestampToken('202004', 'lkdKJ93s', timestamp_token=timestamp_token, use_digest=True)
    user_name_token = TimestampToken(username, password, timestamp_token=timestamp_token, use_digest=use_digest)
    return user_name_token

def get_original_utt(username, password, use_digest=False, ttl=60000):
    timestamp_token = WSU.Timestamp()
    today_datetime = datetime.datetime.today()
    expires_datetime = today_datetime + datetime.timedelta(seconds=60000)
    timestamp_elements = [
#                 WSU.Created(today_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")),
 #                WSU.Expires(expires_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"))
        WSU.Created(format_datetime(today_datetime)),
        WSU.Expires(format_datetime(expires_datetime)),
    ]
    timestamp_token.extend(timestamp_elements)
    user_name_token = UsernameToken(username, password, timestamp_token=timestamp_token,
                                    use_digest=use_digest, nonce=False, zulu_timestamp=True)
    return user_name_token