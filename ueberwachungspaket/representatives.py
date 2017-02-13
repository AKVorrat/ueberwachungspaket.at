from json import load

class Representatives():
    def __init__(self):
        self.parties = load_parties()
        self.teams = load_teams()
        self.representatives = load_representatives(self.parties, self.teams)

    def get_representative_by_idn(self, idn):
        try:
            rep = [rep for rep in self.representatives if rep.idn == idn][0]
        except IndexError:
            rep = None
        return rep

    def get_representative_by_name(self, prettyname):
        try:
            rep = [rep for rep in self.representatives if rep.name.prettyname == prettyname][0]
        except IndexError:
            rep = None
        return rep
    
    def get_party(self, shortname):
        return self.parties[shortname]

class Contact():
    def __init__(self, mail, phone, facebook, twitter):
        self.mail = mail
        self.phone = phone
        self.facebook = facebook
        self.twitter = twitter

class Party():
    def __init__(self, name, shortname, prettyname, color, contact):
        self.name = name
        self.shortname = shortname
        self.prettyname = prettyname
        self.color = color
        self.contact = contact

class Name():
    def __init__(self, firstname, lastname, prettyname, prefix, suffix):
        self.firstname = firstname
        self.lastname = lastname
        self.prettyname = prettyname
        self.prefix = prefix
        self.suffix = suffix

class Image():
    def __init__(self, url, copyright):
        self.url = url
        self.copyright = copyright

class Team():
    def __init__(self, name, prettyname):
        self.name = name
        self.prettyname = prettyname

    def __repr__(self):
        return self.name

class Representative():
    def __init__(self, idn, name, contact, image, party, team, sex, state):
        self.idn = idn
        self.name = name
        self.contact = contact
        self.image = image
        self.party = party
        self.team = team
        self.sex = sex
        self.state = state

        if not self.contact.mail:
            self.contact.mail = party.contact.mail
        if not self.contact.phone:
            self.contact.phone = party.contact.phone
        if not self.contact.facebook:
            self.contact.facebook = party.contact.facebook
        if not self.contact.twitter:
            self.contact.twitter = party.contact.twitter

    def __repr__(self):
        return self.name.firstname + " " + self.name.lastname

    def fullname(self):
        return (self.name.prefix + " " if self.name.prefix else "") + self.name.firstname + " " + self.name.lastname + (" " + self.name.suffix if self.name.suffix else "")

def load_parties():
    parties = {}

    with open("ueberwachungspaket/data/parties.json", "r") as f:
        lparties = load(f)
    
    for prettyname in lparties:
        lparty = lparties[prettyname]
        lcontact = lparty["contact"]
        contact = Contact(lcontact["mail"], lcontact["phone"], lcontact["facebook"], lcontact["twitter"])
        party = Party(lparty["name"], lparty["shortname"], prettyname, lparty["color"], contact)
        parties[prettyname] = party

    return parties

def load_teams():
    teams = {}

    with open("ueberwachungspaket/data/teams.json", "r") as f:
        lteams = load(f)
    
    for prettyname in lteams:
        lteam = lteams[prettyname]
        team = Team(lteam["name"], prettyname)
        teams[prettyname] = team

    return teams

def load_representatives(parties, teams):
    representatives = []

    with open("ueberwachungspaket/data/representatives.json", "r") as f:
        lrepresentatives = load(f)

    for lrep in lrepresentatives:
        lname = lrep["name"]
        name = Name(lname["firstname"], lname["lastname"], lname["prettyname"], lname["prefix"], lname["suffix"])
        lcontact = lrep["contact"]
        contact = Contact(lcontact["mail"], lcontact["phone"], lcontact["facebook"], lcontact["twitter"])
        image = Image(lrep["image"]["url"], lrep["image"]["copyright"])
        party = parties[lrep["party"]]
        team = teams[lrep["team"]]
        representative = Representative(lrep["id"], name, contact, image, party, team, lrep["sex"], lrep["state"])
        representatives.append(representative)

    return representatives
