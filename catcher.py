import sys
from email.generator import Generator
from email.parser import Parser
from aiosmtpd.handlers import Message
from aiosmtpd.controller import Controller


class MailFile(Message):
    def __init__(self, mail_file, message_class=None):
        self.mail_file = mail_file
        super().__init__(message_class=message_class)

    def handle_message(self, message):
        with open(self.mail_file, "w") as f:
            g = Generator(f, mangle_from_=True, maxheaderlen=120)
            g.flatten(message)

    @classmethod
    def from_cli(cls, parser, *args):
        if len(args) < 1:
            parser.error("The file for the mailfile is required")
        elif len(args) > 1:
            parser.error("Too many arguments for Mailbox handler")
        return cls(args[0])


def get_latest_message(mail_file):
    """Returns email.message.Message class object

    Message class can be used like this:
    `message["X-MailFrom"]`
    `message["X-RcptTo"]`
    `message.get_payload() -> str | list[str]`
    `message.is_multipart() -> bool`
    """
    p = Parser()
    with open(mail_file) as f:
        return p.parse(f)


if __name__ == "__main__":
    mail_file = sys.argv[1] if len(sys.argv) > 1 else "rajdhani.mail"

    controller = Controller(MailFile(mail_file), hostname="", port=8025)
    controller.start()

    # controller thread has started
    while True:
        pass
