from backend.models import Template


class Messages():
    MESSAGE = Template.messages.get(id=1).gettext()
    START_COMMAND = Template.messages.get(id=4).gettext()
    WANT_REG = Template.messages.get(id=6).gettext()
    INPUT_NAME = Template.messages.get(id=9).gettext()
    REG_FINISH = Template.messages.get(id=10).gettext()
    NEW_CLIENT_INFO = Template.messages.get(id=11).gettext()
    CLIENT_INFO = Template.messages.get(id=12).gettext()
    HAS_OPEN_ORDERS = Template.messages.get(id=19).gettext()
    ORDER_INFO = Template.messages.get(id=20).gettext()
    REFERAL_PROGRAM = Template.messages.get(id=21).gettext()
    RECALC_BONUS_SUCCESS = Template.messages.get(id=25).gettext()
    REFERAL_INFO = Template.messages.get(id=26).gettext()
    CONTACTS = Template.messages.get(id=27).gettext()
    WAITING_FOR_OPEN_ORDERS = Template.messages.get(id=28).gettext()
    LINK_ADMINISTRATOR = Template.messages.get(id=29).gettext()
    LINK_MASTER = Template.messages.get(id=30).gettext()
    DISCOUNTS = Template.messages.get(id=32).gettext()
    BONUSES_ACCRUED = Template.messages.get(id=33).gettext()
    OPEN_ORDERS_EMPTY = Template.messages.get(id=34).gettext()


class Keys():
    KEY = Template.keys.get(id=2).gettext()
    SEND_CONTACT = Template.keys.get(id=5).gettext()
    YES = Template.keys.get(id=7).gettext()
    NO = Template.keys.get(id=8).gettext()
    OPEN_ORDERS = Template.keys.get(id=13).gettext()
    CONTACT_ADMINISTRATOR = Template.keys.get(id=14).gettext()
    CONSULTATION_WITH_MASTER = Template.keys.get(id=15).gettext()
    REFERAL_PROGRAM = Template.keys.get(id=16).gettext()
    CONTACTS = Template.keys.get(id=17).gettext()
    MENU = Template.keys.get(id=18).gettext()
    BACK = Template.keys.get(id=22).gettext()
    REFERALS = Template.keys.get(id=23).gettext()
    RECALC_BONUS = Template.keys.get(id=24).gettext()
    DISCOUNTS = Template.keys.get(id=31).gettext()


class Smiles():
    SMILES = Template.smiles.get(id=3).gettext()
