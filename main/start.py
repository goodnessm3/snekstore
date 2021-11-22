from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, current_app
import main.fxns
import main.random_image
from main.db import get_db
import secrets
import os

bp = Blueprint('lookup_page', __name__, url_prefix='')


def sanitize(astr):

    allowed = [" ", "'", "!", "?", "@"]
    cnt = 0
    out = ""
    for x in astr:
        y = ord(x)
        if (64 < y < 91) or (96 < y < 123) or (47 < y < 58) or x in allowed:
            out += x
            cnt += 1
        if cnt > 256:
            break
    return out


@bp.route('/', methods=('GET', 'POST'))
def begin():

    session.permanent = True
    error = None
    db = get_db()
    cur = db.cursor()
    if not "tok" in session:
        session["tok"] = secrets.token_hex(16)

    if request.method == 'POST':

        query = request.form['qry']

        cur.execute('''SELECT uname FROM shop WHERE rand = ?''', (query,))
        result = cur.fetchone()
        print(result)
        if result:
            cur.execute('''UPDATE shop SET cookie = ? WHERE rand = ?''', (session["tok"], query))
            cur.execute('''UPDATE shop SET rand = NULL WHERE cookie = ?''', (session["tok"],))
            # need to remove this otherwise if snek by chance generated the same random number twice,
            # a user's entry would be overridden by the later number. We now exclusively use the cookie ID
            # to identify the user.
            print("authenticated new user")
            db.commit()
            return redirect(url_for("lookup_page.store"))

        else:
            error = "That code doesn't match anything Snek is expecting to see."

    if request.method == 'GET':

        cur.execute('''SELECT uname FROM shop WHERE cookie = ?''', (session["tok"],))
        result = cur.fetchone()
        if result:
            return redirect(url_for("lookup_page.store"))

    if error:
        flash(error)
    return render_template('page1/page1.html')


@bp.route('/store', methods=('GET', 'POST'))
def store():

    session.permanent = True
    if not "tok" in session:
        return redirect(url_for("lookup_page.begin"))
        # send user to registration page if no cookie

    error = None
    db = get_db()
    cur = db.cursor()

    # we'll need this info regardless for various things

    tok = session["tok"]
    cur.execute('''SELECT uid, uname FROM shop WHERE cookie = ?''', (tok,))
    res = cur.fetchone()
    if not res:
        return redirect(url_for("lookup_page.begin"))  # user has a token but didn't authenticate yet
    uid, uname = res  # use the internet table to get the discord ID and then use that for other lookups
    session["uname"] = uname
    cur.execute('''SELECT bux FROM stats WHERE uid = ?''', (uid,))
    session["balance"], = cur.fetchone()
    # super clever technique of unpacking of single-value tuple, for real tough guys only

    if request.method == 'POST':
        print(request.form)
        san = sanitize(request.form["msg"])
        with open(current_app.config["SHOP_FILE"], "a") as f:
            if request.form["type"] == "sendmessage":
                channelid = current_app.config["MESSAGE_CHANNELS"][request.form["chan"]]
                f.write(request.form["type"] + "||" + str(uid) + "||" + str(channelid) + "||" + san + os.linesep)
                session["balance"] -= 1000
                # we need to manually modify the displayed balance on the basis of what was just submitted
                # because there's a delay in snek reading the shop file and writing the change to the db
            elif request.form["type"] == "namechange":
                f.write(request.form["type"] + "||" + str(uid) + "||" + san + os.linesep)
                session["balance"] -= 10000
            elif request.form["type"] == "ssrbirb":
                channelid = current_app.config["MESSAGE_CHANNELS"][request.form["chan"]]
                f.write(request.form["type"] + "||" + str(uid) + "||" + str(channelid) + os.linesep)
                session["balance"] -= 75000



    return render_template('storepage/store.html',
                           chans=[x for x in current_app.config["MESSAGE_CHANNELS"].keys()])
