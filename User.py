#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,request,redirect,url_for,session,flash
import pymysql
from config import *

con = pymysql.connect(HOST,USER,PASS,DATABASE)
user = Blueprint('user',__name__)

@user.route("/loginpage")
def Loginpage():
    if "username" not in session:
        return render_template("login/login.html",headername="Login เข้าใช้งานระบบ")
    else:
        return redirect(url_for('member.Showdatamember'))
@user.route("/checklogin",methods=["POST"])
def Checklogin():
    username = request.form['username']
    password = request.form['password']
    with con:
        cur = con.cursor()
        sql = "SELECT * FROM tb_user WHERE usr_username = %s AND usr_password = %s and usr_status=1"
        cur.execute(sql,(username,password))
        rows = cur.fetchall()
        cur.close()
        if len(rows) > 0:
            session['username'] = username
            session['fname'] = rows[0][1]
            session['lname'] = rows[0][2]
            session.permanent = True
            return redirect(url_for('member.Showdatamember'))
        else:
            flash("ไม่พบข้อมูลในระบบ")
            return render_template('login/login.html',headername="Login เข้าใช้งานระบบ")
@user.route("/logoff")
def Logoff():
    session.clear()
    return redirect(url_for('user.Loginpage'))

@user.route("/regisuser")
def Regisuser():
    return render_template('user/adduser.html',headername="สมัครสมาชิก")

@user.route("/adduser",methods=["POST"])
def Adduser():
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        username = request.form["username"]
        password = request.form["password"]
        repassword = request.form["repassword"]

        with con:
            cur = con.cursor()
            sql = "SELECT * FROM tb_user WHERE usr_username = %s"
            cur.execute(sql,(username))
            rows = cur.fetchall()
            cur.close()
            if len(rows) >0:
                flash("Username ซ้ำในระบบ กรุณาแก้ไข username")
                return render_template('user/adduser.html',headername="สมัครสมาชิก")
        if password != repassword:
            flash("คุณกรอก password และ repassword ไม่เหมือนกัน")
            return render_template('user/adduser.html',headername="สมัครสมาชิก")
        with con:
            cur = con.cursor()
            sql = "insert into tb_user (usr_fname,usr_lname,usr_username,usr_password) values(%s,%s,%s,%s)"
            cur.execute(sql,(fname,lname,username,password))
            con.commit()
            cur.close()
            flash("สมัครสมาชิกแล้ว รอผู้ดูแลตรวจสอบ")
            return render_template('login/login.html',headername="สมัครสมาชิก",status="wait")
