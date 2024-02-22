from requests import Session

session = Session()
session.verify = False  # "my_certs/certificate.pem"
from lxml.etree import QName
import os, shutil
import uuid

from lxml import etree
from lxml.builder import ElementMaker

from zeep import ns
from zeep.plugins import Plugin
from zeep.wsdl.utils import get_or_create_header


class XMLNamespaces:
    s = 'http://www.w3.org/2003/05/soap-envelope'
    a = 'http://www.w3.org/2005/08/addressing'
    wsse = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
    wsu = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"


def apply_wsses(wsses, envelope, http_headers):
    # Apply WSSE
    if wsses:
        if isinstance(wsses, list):
            iwsse = 1
            for wsse in wsses:
                envelope, http_headers = wsse.apply(envelope, http_headers)
                CertPlugin.dump_xml(envelope, os.path.join("outputs", f"after_wsse_{iwsse}.xml"))
                iwsse += 1
        else:
            envelope, http_headers = wsses.apply(envelope, http_headers)
            CertPlugin.dump_xml(envelope, os.path.join("outputs", "after_wsses.xml"))

    return envelope, http_headers


def ksign_envelope(envelope,
                   key_file,
                   certfile,
                   password=None,
                   signature_method=None,
                   digest_method=None,
                   ):
    from zeep.wsse import signature
    key = signature._make_sign_key(signature._read_file(key_file), signature._read_file(certfile), password)
    return signature._sign_envelope_with_key(envelope, key, signature_method, digest_method)


def kbsign_envelope(envelope,
                    key_file,
                    certfile,
                    password=None,
                    signature_method=None,
                    digest_method=None,
                    ):
    from zeep.wsse import signature
    key = signature._make_sign_key(signature._read_file(key_file), signature._read_file(certfile), password)
    return signature._sign_envelope_with_key_binary(envelope, key, signature_method, digest_method)


class CertPlugin(Plugin):
    def __init__(self, certfile, key_file, password=None, pkcs12=True):
        # key format can be privkey-pem or pkcs8-der
        self.certfile = certfile
        self.key_file = key_file
        self.password = password
        if password:
            suffix = f" --pwd {password}"
        else:
            suffix = ""
        if pkcs12:
            self.certargs = f"--pkcs12 \"{self.key_file}\"{suffix}"
        else:
            self.certargs = f"--privkey-pem \"{self.key_file}\" --pubkey-cert-pem \"{self.certfile}\"{suffix}"
            assert cert_key_matches(self.certfile, self.key_file, password), "Cert and key do not match"
        super().__init__()

    @staticmethod
    def dump_xml(envelope, filename):
        #print("dump_xml", filename)
        with open(filename, "wb") as f:
            f.write(etree.tostring(envelope, pretty_print=True))

    @staticmethod
    def read_xml(file_like_or_string):
        """Read an XML file and return an etree object.
        file_like_or_string can be a string with the file contents, or a file-like object for reading XML contents."""
        #with open(filename, "rb") as f:
        if hasattr(file_like_or_string, "read"):
            return etree.parse(file_like_or_string).getroot()
        else:
            return etree.fromstring(file_like_or_string)

    def sign_file(self, args, filename, out_file):
        if os.path.exists(out_file):
            os.remove(out_file)
        signcmd = f"xmlsec1 --sign {self.certargs} --output {out_file} {args} {filename}"
        print("signcmd", signcmd)
        os.system(signcmd)

    def verify(self, veryfy_args, filename):
        verifcmd = f"xmlsec1 --verify {self.certargs} {veryfy_args} {filename}"
        print("verifcmd", verifcmd)
        os.system(verifcmd)

    def kbsign_envelope(self, xml_root_element):
        signed = kbsign_envelope(xml_root_element, self.key_file, self.certfile)

        tree = etree.ElementTree(xml_root_element)
        tree.write(os.path.join("outputs", 'signed-soapenv.xml'))

        with open(os.path.join("outputs", "signed-soapenv.xml"), "rb") as f:
            return etree.parse(f)


def replace_xpath_args(envelope, expression, attribute, value):
    csbod = envelope.xpath(expression)[0]
    csbod.attrib[attribute] = value


class MyLoggingPlugin(CertPlugin):

    def __init__(self, wsses, certfile, key_file, password=None, pkcs12=True, xmlsec_sign=False,
                 xmlsec_verify=True, body_id=None, signature_template=None, xml_file=None):
        # key format can be privkey-pem or pkcs8-der
        CertPlugin.__init__(self, certfile, key_file, password=password, pkcs12=pkcs12)
        self.wsses = wsses
        self.xmlsec_sign = xmlsec_sign
        self.xmlsec_verify = xmlsec_verify
        self.body_id = body_id
        self.signature_template = signature_template
        self.xml_file = xml_file
        #print("mlp", self.wsses, self.xmlsec_sign, self.body_id, self.signature_template)

    def egress(self, envelope, http_headers, operation, binding_options):
        self.dump_xml(envelope, os.path.join("outputs","raw_xml.xml"))
        security_header_xpath = "///*[local-name()='Envelope']/*[local-name()='Header']/*[local-name()='Security']"
        header_xpath = "///*[local-name()='Envelope']/*[local-name()='Header']"
        envelope_xpath = "///*[local-name()='Envelope']"
        if self.xml_file is not None:
            envelope = self.read_xml(self.xml_file)
        header = get_or_create_header(envelope)

        wsa_action = operation.abstract.wsa_action
        if not wsa_action:
            wsa_action = operation.soapaction

        headers = [
            WSA.Action(wsa_action),
            WSA.MessageID("urn:uuid:" + str(uuid.uuid4())),
            #WSA.To(self.address_url or binding_options["address"]),
            WSA.To(None or binding_options["address"]),
        ]
        header.extend(headers)

        if self.signature_template is not None:
            with open(self.signature_template, "rb") as f:
                signature_template_xml = etree.parse(f)
                stsec = signature_template_xml.getroot().xpath(security_header_xpath)
                print("stsec", stsec)
            sec = envelope.xpath(header_xpath)
            print("secs", sec, list(sec), list(sec[0]))
            sec[0].append(stsec[0])
        self.dump_xml(envelope, os.path.join("outputs","joined.xml"))
        if self.body_id is not None:
            replace_xpath_args(envelope, "///*[local-name()='Envelope']/*[local-name()='Body']",
                                    QName(XMLNamespaces.wsu, 'Id'), self.body_id)
        self.dump_xml(envelope, os.path.join("outputs","joined_ids.xml"))

        if self.wsses is not None:
            envelope, http_headers = apply_wsses(self.wsses, envelope, http_headers)
        #self.kbsign_envelope(envelope)
        self.dump_xml(envelope, os.path.join("outputs", "short.xml"))
        prettify_xml_file(os.path.join("outputs", "short.xml"), os.path.join("outputs", "short_pretty.xml"))

        args = " --id-attr:Id Body --id-attr:Id Timestamp --store-references "
        #args = " --id-attr:Id Body --id-attr:Id Timestamp --id-attr:Id BinarySecurityToken"
        #args = " --id-attr:Id Body --id-attr:Id Timestamp --id-attr:Id BinarySecurityToken --id-attr:Id Security"
        verify_args = args
        filename = os.path.join("outputs", "short.xml")
        if self.xmlsec_sign:
            verify_filename = os.path.join("outputs", "signed_xml.xml")
            self.sign_file(args, filename, verify_filename)
            prettify_xml_file(verify_filename, os.path.join("outputs", "signed_xml_pretty.xml"))
        else:
            verify_filename = os.path.join("outputs", "short.xml")
        if self.xmlsec_verify:
            self.verify(verify_args, verify_filename)
        if self.xmlsec_sign:
            with open(os.path.join("outputs", "signed_xml.xml"), "rb") as f:
                return etree.parse(f), http_headers
            return self.read_xml(os.path.join("outputs", "signed_xml.xml")), http_headers
        else:
            return envelope, http_headers

class BodyReplacementPlugin(Plugin):
    def __init__(self, body_id=None, xmlsec_verify=True):
        self.body_id = body_id
        self.xmlsec_verify = xmlsec_verify
    def egress(self, envelope, http_headers, operation, binding_options):
        if self.body_id is not None:
            replace_xpath_args(envelope, "///*[local-name()='Envelope']/*[local-name()='Body']",

                                    QName(XMLNamespaces.wsu, 'Id'), self.body_id)


class MyGettingPlugin(CertPlugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        # verify_args = " --id-attr:Id Body --id-attr:Id Timestamp "
        verify_args = " --id-attr:id Body --id-attr:id Timestamp "
        # verify_args = " --id-attr:id Body"
        # verify_args = " "
        # verify_args = " --id-attr:Id Body "
        # self.sign_file(args, filename, verify_filename)
        self.verify(verify_args, self.filename)
        return self.read_xml(self.filename), http_headers

    def __init__(self, filename="xmlsec_sign.xml", signed_filename="short_signed.xml", **kwargs):
        self.filename = filename
        self.signed_filename = signed_filename
        self.xmlsec_verify = kwargs.get("xmlsec_verify", True)
        CertPlugin.__init__(self, **kwargs)


class MySigningPlugin(CertPlugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        args = " --id-attr:id Body --id-attr:id Timestamp "
        verify_args = args
        # verify_args = " --id-attr:Id Body "
        self.sign_file(args, self.filename, self.signed_filename)
        self.verify(verify_args, self.signed_filename)
        return self.read_xml(self.signed_filename), http_headers

    def __init__(self, filename="signed_xml.xml", signed_filename="short_signed.xml", **kwargs):
        self.filename = filename
        self.signed_filename = signed_filename
        CertPlugin.__init__(self, **kwargs)


class MyCopyingPlugin(CertPlugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        print("copying", self.filename, self.to_filename)
        shutil.copy(self.filename, self.to_filename)

    def __init__(self, filename="signed_xml.xml", to_filename="short_signed.xml", **kwargs):
        self.filename = filename
        self.to_filename = to_filename
        CertPlugin.__init__(self, **kwargs)


def prettify_xml_file(xmlfile, outfile):
    print("prettify_xml_file", xmlfile, outfile)
    with open(xmlfile, "rb") as f:
        xml_string = f.read()
    with open(outfile, "wb") as f:
        f.write(prettify_xml(xml_string))


def prettify_xml(xml_string):
    return etree.tostring(etree.fromstring(xml_string), pretty_print=True)


def prettify_etree(etree_obj):
    return etree.tostring(etree_obj, pretty_print=True)


def cert_key_matches(certfile, key_file, password):
    from OpenSSL.crypto import load_certificate, load_privatekey, FILETYPE_PEM
    from OpenSSL.crypto import dump_certificate, dump_privatekey, dump_publickey, FILETYPE_PEM, FILETYPE_ASN1
    import OpenSSL.SSL
    with open(certfile, 'rb') as f:
        cert = load_certificate(FILETYPE_PEM, f.read())
    with open(key_file, 'rb') as f:
        key = load_privatekey(FILETYPE_PEM, f.read(), passphrase=password)
    context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
    context.use_privatekey(key)
    context.use_certificate(cert)
    try:
        context.check_privatekey()
        return True
    except OpenSSL.SSL.Error:
        return False


def cert_to_pem(certfile):
    from OpenSSL.crypto import load_certificate, FILETYPE_PEM
    with open(certfile, 'rb') as f:
        cert = load_certificate(FILETYPE_PEM, f.read())
    return cert


WSA = ElementMaker(namespace=ns.WSA, nsmap={"wsa": ns.WSA})


class WsAddressingPlugin(Plugin):
    nsmap = {"wsa": ns.WSA}

    def __init__(self, address_url: str = None):
        self.address_url = address_url

    def egress(self, envelope, http_headers, operation, binding_options):
        """Apply the ws-addressing headers to the given envelope."""

        wsa_action = operation.abstract.wsa_action
        if not wsa_action:
            wsa_action = operation.soapaction

        header = get_or_create_header(envelope)
        headers = [
            WSA.Action(wsa_action),
            WSA.MessageID("urn:uuid:" + str(uuid.uuid4())),
            WSA.To(self.address_url or binding_options["address"]),
        ]
        header.extend(headers)

        # the top_nsmap kwarg was added in lxml 3.5.0
        if etree.LXML_VERSION[:2] >= (3, 5):
            etree.cleanup_namespaces(
                header, keep_ns_prefixes=header.nsmap, top_nsmap=self.nsmap
            )
        else:
            etree.cleanup_namespaces(header)
        return envelope, http_headers
