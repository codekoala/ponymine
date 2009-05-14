import poplib

def check_mail(user, passwd, server='localhost', ssl=False, port=110):
    # connect to the server
    mailbox = ssl and poplib.POP3_SSL(server, port) or poplib.POP3(server, port)

    # login
    mailbox.user(user)
    mailbox.pass_(passwd)

    # get messages
    message_count = len(mailbox.list()[1])
    for i in range(message_count):
        for m in mailbox.retr(i + 1)[1]:
            print m

if __name__ == '__main__':
    check_mail('wheaties_')