#-*- coding: utf-8 -*-

MAIL_DISCLAIMER = "Diese E-Mail wird übermittelt im Namen von: {name_user}, {mail_user}"

MAIL_REPRESENTATIVE = """
{salutation} {name_rep}, 

das geplante Überwachungspaket im neuen Regierungsprogramm vom 30. Jänner 2017 erfüllt mich mit großer Besorgnis. Die vorgeschlagenen Maßnahmen laufen auf eine Totalüberwachung aller Menschen in Österreich hinaus. Egal ob man mit dem Auto fährt, öffentliche Verkehrsmittel verwendet, sich auf öffentlichen Plätzen bewegt, oder zu den 4,5 Millionen Menschen mit anonymen SIM Karten zählt: Bald soll die gesamte Bevölkerung auf Schritt und Tritt überwacht werden. Das will ich nicht! Ich habe ein Recht auf Privatsphäre.

Für keine der vorgestellten Maßnahmen wurden Belege geliefert, dass sie tatsächlich einen Sicherheitsgewinn bringen. Sicher ist nur, dass mit ihnen meine Freiheit eingeschränkt wird. 

Videoüberwachung kann Terroristen sogar motivieren, da damit Bilder von ihnen und ihren Gräueltaten in die Öffentlichkeit gelangen. Die Registrierung von Prepaid-SIM-Karten wurde bereits in vielen Ländern geprüft und abgelehnt; sogar die EU Innenkommissarin hat sich dagegen ausgesprochen. 

Wieso wollen Sie meine reale Freiheit einem subjektiven Sicherheitsgefühl opfern? 

Es ist die Aufgabe des Staates, die Bevölkerung zu schützen. Dazu gehört auch die Wahrung der Grundrechte. Bitte sprechen Sie sich Sie gegen das Überwachungspaket aus! Verhindern Sie die Einrichtung eines lückenlosen Überwachungssystems! Setzen Sie sich für Grund- und Freiheitsrechte ein!

Hochachtungsvoll
{name_user}
"""

MAIL_WELCOME = """
Liebe/r {name_user}, 

wir danken Ihnen herzlich, dass Sie sich für Ihr Grundrecht auf Privatsphäre und Datenschutz stark gemacht haben. Wir würden uns sehr freuen, wenn Sie mithelfen, dass möglichst viele Menschen vom geplanten Überwachungspaket erfahren. Wir alle sind davon betroffen und gemeinsam können wir etwas für unsere Freiheit tun.

1))) Erzählen Sie ihren Freunden von Ihrem Engagement! 
Facebook: https://www.facebook.com/epicenter.works/photos/a.613435972043996.1073741825.164063546981243/1285542684833318/?type=3&theater
Twitter: https://twitter.com/epicenter_works/status/839740869683077120

2))) Senden Sie eine E-Mail an fünf Freunde. Hier ist ein Textvorschlag dafür: 
"
Hallo, 

ich habe gerade meinen Abgeordneten wegen des geplanten Überwachungspakets kontaktiert. Die Regierung will uns alle mit lückenloser Überwachung unter Generalverdacht stellen. 

Bitte schau dir www.überwachungspaket.at an und werde selbst für deine Rechte aktiv.

Hilf mit, unsere Privatsphäre zu retten!

Liebe Grüße,
" 

3))) Gehen Sie den nächsten Schritt! Rufen Sie Ihre Abgeordneten an! 
Die effektivste Art, Politikern ins Gewissen zu reden ist, direkt mit ihnen am Telefon zu sprechen.
Mit unserer Hotline geht das ganz einfach. Rufen Sie 
0720 205088
an und folgen Sie dem Sprachmenü.
Mit einer Anruferinnerung leisten Sie einen wiederkehrenden Beitrag, die Überwachungspläne der Bundesregierung zu verhindern!  


Zivilgesellschaft wirkt! 
Unser Verein epicenter.works kämpft für den Erhalt von Grund- und Freiheitsrechten im Internet. Wir streiten vor Gericht, im Parlament und auf der Straße. Wir arbeiten unabhängig von Parteien und Unternehmen. Damit wir weiterhin schlagkräftig bleiben, sind wir auf Hilfe aus der Zivilgesellschaft angewiesen. 
Sie können uns als Fördermitglied oder mit einer Spende unterstützen: spenden.epicenter.works.


Liebe Grüße, 

Ihr Team von epicenter.works
"""

MAIL_VALIDATE = """
Liebe/r {name_user},

vielen Dank für Ihren Einsatz für unsere Grundrechte! Damit Ihre E-Mail über www.überwachungspaket.at auch abgeschickt werden kann, müssen Sie diesem Link folgen:
{url}

Falls Sie nicht wissen, wieso sie diese Nachricht erhalten haben, bitte ignorieren Sie diese Nachricht.

Liebe Grüße,

Ihr Team von epicenter.works
"""

CONSULTATION_MAIL_VALIDATE = """
Liebe/r {first_name} {last_name},

vielen Dank für Ihren Einsatz für unsere Grundrechte! Damit Ihre Stellungnahme über www.überwachungspaket.at auch abgeschickt werden kann, müssen Sie diesem Link folgen:
{url}

Falls Sie nicht wissen, wieso sie diese Nachricht erhalten haben, bitte ignorieren Sie diese Nachricht.

Liebe Grüße,

Ihr Team von epicenter.works
"""

CONSULTATION_PDF_BMI_FRAME = """
<html>
<head>
<meta charset="utf-8">
<style type="text/css">
body { font-family: sans-serif; }
#header { font-weight: bold; margin-bottom: 2cm; }
#date { text-align: right; margin-top: 2cm; margin-bottom: 2cm; }
#intro { margin-bottom: 2cm; }
#endnotes { margin-top: 2cm; }
h1 { font-size: large }
h2 { font-size: large }
</style>
</head>
<body>
<div id="header">
<p>%s<p>
<p id="date">%s</p>
<p id="intro">%s nimmt zu dem Entwurf wie folgt Stellung:</p>
<h1>Stellungnahme im Begutachtungsverfahren zum Ministerialentwurf des Innenministeriums, mit dem das Sicherheitspolizeigesetzes, das Bundesstraßen-Mautgesetzes 2002, die Straßenverkehrsordnung 1960 und das Telekommunikationsgesetzes 2003 geändert werden (326/ME)</h1>
</div>
%s
<div id="endnotes">
%s
</div>
</body>
</html>"""

CONSULTATION_PDF_BMJ_FRAME = """
<html>
<head>
<meta charset="utf-8">
<style type="text/css">
body { font-family: sans-serif; }
#header { font-weight: bold; margin-bottom: 2cm; }
#date { text-align: right; margin-top: 2cm; margin-bottom: 2cm; }
#intro { margin-bottom: 2cm; }
#endnotes { margin-top: 2cm; }
h1 { font-size: large }
h2 { font-size: large }
</style>
</head>
<body>
<div id="header">
<p>%s<p>
<p id="date">%s</p>
<p id="intro">%s nimmt zu dem Entwurf wie folgt Stellung:</p>
<h1>Stellungnahme im Begutachtungsverfahren zum Ministerialentwurf des Justizministeriums, Strafprozessrechtsänderungsgesetz 2017 (325/ME)</h1>
</div>
%s
<div id="endnotes">
%s
</div>
</body>
</html>"""
 

CONSULTATION_INTRO = """Sehr geehrte Damen und Herren,

wir übersenden Ihnen die angehängte Stellungnahme zum Ministerialentwurf %s im Namen von %s. %s

Für Rückfragen wenden Sie sich bitte direkt an %s via <%s>.

Mit freundlichen Grüßen,
das Team von epicenter.works"""
