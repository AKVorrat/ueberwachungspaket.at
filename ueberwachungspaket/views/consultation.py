from random import shuffle
from json import load
from flask import (Blueprint, render_template, request, jsonify,
                   send_from_directory)
from sqlalchemy import and_
from config import *
from config.main import *
from config.mail import *
from database.models import Opinion
from database import db_session

mod = Blueprint("consultation", __name__, url_prefix="/konsultation")
page_size = 35


@mod.route("/")
def index():
    with open("ueberwachungspaket/data/quotes.json", "r") as json_file:
        quotes = load(json_file)
    shuffle(quotes)
    query = db_session.query(Opinion).order_by(Opinion.originality.desc(), Opinion.date.desc())
    opinions_count = query.count()
    opinions = query.limit(page_size).all()

    return render_template(
        "consultation/index.html",
        quotes=quotes,
        opinions=opinions,
        opinions_count=opinions_count
    )


@mod.route("/load")
def consultation_load():
    page_index = request.args.get("pageIndex", 0, type=int)
    sort_key = request.args.get("sortKey")
    filter_origin = request.args.get("filterOrigin")
    filter_topic = request.args.get("filterTopic")
    filter_name = request.args.get("filterName")

    query = db_session.query(Opinion)

    if sort_key:
        if sort_key == "name":
            query = query.order_by(Opinion.name, Opinion.originality.desc())
        if sort_key == "-name":
            query = query.order_by(Opinion.name.desc(), Opinion.originality.desc())
        elif sort_key == "date":
            query = query.order_by(Opinion.date, Opinion.originality.desc())
        elif sort_key == "-date":
            query = query.order_by(Opinion.date.desc(), Opinion.originality.desc())
        elif sort_key == "-originality":
            query = query.order_by(Opinion.originality, Opinion.date.desc())
        else:
            query = query.order_by(Opinion.originality.desc(), Opinion.date.desc())

    if filter_topic:
        if filter_topic == "bundestrojaner":
            query = query.filter_by(addresses_bundestrojaner=True)
        elif filter_topic == "netzsperren":
            query = query.filter_by(addresses_netzsperren=True)
        elif filter_topic == "vds-video":
            query = query.filter_by(addresses_vds_video=True)
        elif filter_topic == "ueberwachung-strassen":
            query = query.filter_by(addresses_ueberwachung_strassen=True)
        elif filter_topic == "vds-quickfreeze":
            query = query.filter_by(addresses_vds_quickfreeze=True)
        elif filter_topic == "anonyme-simkarten":
            query = query.filter_by(addresses_anonyme_simkarten=True)
        elif filter_topic == "imsi-catcher":
            query = query.filter_by(addresses_imsi_catcher=True)
        elif filter_topic == "lauschangriff-auto":
            query = query.filter_by(addresses_lauschangriff_auto=True)

    if filter_origin:
        if filter_origin == "bmi":
            query = query.filter(and_(Opinion.link_bmi_pdf.isnot(None), Opinion.link_bmi_pdf != ""))
        elif filter_origin == "bmj":
            query = query.filter(and_(Opinion.link_bmj_pdf.isnot(None), Opinion.link_bmj_pdf != ""))

    if filter_name:
        query = query.filter(Opinion.name.ilike("%{}%".format(filter_name)))

    opinions_count = query.count()
    opinions = query.slice(page_index * page_size, (page_index + 1) * page_size).all()
    opinions = [opinion.serialize() for opinion in opinions]
    return jsonify(opinions=opinions, count=opinions_count)


@mod.route("/stats")
def consultation_stats():
    query = db_session.query(Opinion)
    stats = {
        "addressesBundestrojaner": query.filter_by(addresses_bundestrojaner=True).count(),
        "addressesNetzsperren": query.filter_by(addresses_netzsperren=True).count(),
        "addressesVdsVideo": query.filter_by(addresses_vds_video=True).count(),
        "addressesUeberwachungStrassen": query.filter_by(addresses_ueberwachung_strassen=True).count(),
        "addressesVdsQuickfreeze": query.filter_by(addresses_vds_quickfreeze=True).count(),
        "addressesAnonymeSimkarten": query.filter_by(addresses_anonyme_simkarten=True).count(),
        "addressesImsiCatcher": query.filter_by(addresses_imsi_catcher=True).count(),
        "addressesLauschangriffAuto": query.filter_by(addresses_lauschangriff_auto=True).count()
    }
    return jsonify(stats=stats)


@mod.route("/showpdf/bmi/<int:fid>")
def showpdf_bmi(fid):
    resp = send_from_directory(PDF_FOLDER, str(fid) + "_bmi.pdf")
    resp.headers["Content-Disposition"] = "inline; filename=" + str(fid) + "_bmi.pdf"
    return resp


@mod.route("/showpdf/bmj/<int:fid>")
def showpdf_bmj(fid):
    resp = send_from_directory(PDF_FOLDER, str(fid) + "_bmj.pdf")
    resp.headers["Content-Disposition"] = "inline; filename=" + str(fid) + "_bmj.pdf"
    return resp
