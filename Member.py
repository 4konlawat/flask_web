#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,request,redirect,url_for,session,jsonify,make_response
import pymysql
from config import *
import os
import json
from flask_paginate import Pagination,get_page_args
import pdfkit

con = pymysql.connect(HOST,USER,PASS,DATABASE)
member = Blueprint('member',__name__)
@member.route("/showmember")
def Showdatamember():
    if "username" not in session:
        return render_template('login/login.html',headername="Login เข้าใช้งานระบบ")
    con.connect()
    cur = con.cursor()
    sql = "SELECT * FROM tb_member"
    cur.execute(sql)
    rows = cur.fetchall()

    users = list(range(len(rows)))
    total = len(rows)
    page,per_page,offset = get_page_args(page_parameter='page',per_page_parameter='per_page')
    getuser = users[offset:offset+5]
    Pagination_users = getuser
    pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')
    
    return render_template("member/showdatamember.html",headername="ข้อมูลสมาชิก",datas=rows,
    users=Pagination_users,page=page,per_page=per_page,pagination=pagination,len=total)



@member.route("/showsearch",methods=["POST"])
def Showsearch():
    if "username" not in session:
        return render_template('login/login.html',headername="Login เข้าใช้งานระบบ")
    with con:
        if request.method == "POST":
            KeySearch = request.form['searchname']
            likeString = "%" + KeySearch +"%"
            cur = con.cursor()
            sql = "SELECT * FROM tb_member where mem_fname like %s or mem_lname like %s"
            cur.execute(sql,(likeString,likeString))
            rows = cur.fetchall()
            cur.close()
            return render_template("member/showdatamember.html",headername="ข้อมูลสมาชิก",datas=rows)

@member.route("/showwithdate",methods=["POST"])
def Showwithdate():
    if "username" not in session:
        return render_template('login/login.html',headername="Login เข้าใช้งานระบบ")
    if request.method == "POST":
        dstart = request.form['dtstart']
        dtend = request.form['dtend']
        with con:
            cur = con.cursor()
            sql = "SELECT * FROM tb_member where mem_birdthdate between %s and %s"
            cur.execute(sql,(dstart,dtend))
            rows = cur.fetchall()
            cur.close()
            return render_template("member/showdatamember.html",headername="ข้อมูลสมาชิก",datas=rows)
@member.route("/editmember",methods=["POST"])
def Editmember():
    if request.method == "POST":
        id = request.form["id"]
        fname = request.form["fname"]
        lname = request.form["lname"]
        sex = request.form["sex"]
        bdate = request.form["bdate"]
        email = request.form["email"]
        file = request.files['files']

        if file.filename =="":
            with con:
                #update with nopic
                cur = con.cursor()
                sql = "update tb_member set mem_fname = %s,mem_lname = %s,mem_sex = %s,mem_birdthdate = %s,mem_email = %s where mem_id = %s"
                cur.execute(sql,(fname,lname,sex,bdate,email,id))
                con.commit()
                cur.close()
                return redirect(url_for('member.Showdatamember'))
        else:
                #update with pic
            file = request.files['files']
            upload_folder = 'static/images'
            app_folder = os.path.dirname(__file__)
            img_folder = os.path.join(app_folder,upload_folder)
            file.save(os.path.join(img_folder,file.filename))
            path = upload_folder + "/" + file.filename
            with con:
                cur = con.cursor()
                sql = "update tb_member set mem_fname = %s,mem_lname = %s,mem_sex = %s,mem_birdthdate = %s,mem_email = %s , mem_pic =%s where mem_id = %s"
                cur.execute(sql,(fname,lname,sex,bdate,email,path,id))
                con.commit()
                cur.close()
                return redirect(url_for('member.Showdatamember'))

@member.route("/delmember",methods=["POST"])
def Delmember():
    if request.method == "POST":
        id = request.form['id']
        with con:
            cur = con.cursor()
            sql = "delete from tb_member where mem_id = %s"
            cur.execute(sql,(id))
            con.commit()
            cur.close()
            return redirect(url_for('member.Showdatamember'))

@member.route("/adddatamember")
def Adddatamember():
    if "username" not in session:
        return render_template('login/login.html',headername="Login เข้าใช้งานระบบ")
    return render_template("member/adddatamember.html",headername="เพิ่มข้อมูลสมาชิก")

@member.route("/adddata",methods=["POST"])
def Adddata():
    if request.method == "POST":
        file = request.files['files']
        upload_folder = 'static/images'
        app_folder = os.path.dirname(__file__)
        img_folder = os.path.join(app_folder,upload_folder)
        file.save(os.path.join(img_folder,file.filename))
        path = upload_folder + "/" + file.filename
        fname = request.form["fname"]
        lname = request.form["lname"]
        sex = request.form["sex"]
        bdate = request.form["bdate"]
        email = request.form["email"]
        with con:
            cur = con.cursor()
            sql = "insert into tb_member (mem_fname,mem_lname,mem_sex,mem_birdthdate,mem_email,mem_pic) VALUES (%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(fname,lname,sex,bdate,email,path))
            con.commit()
            cur.close()
            return redirect(url_for('member.Showdatamember'))

################## REPORT 

@member.route("/report",methods=["POST"])
def Report():
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    if request.method == "POST":
        with con:
            sex = request.form['sex']
            cur = con.cursor()
            sql = "SELECT * FROM tb_member where mem_sex = %s"
            cur.execute(sql,(sex))
            rows = cur.fetchall()
            cur.close()

            render = render_template("member/showreport.html",headername="รายงานรายชื่อ",datas=rows,sum=len(rows))
            pdf = pdfkit.from_string(render,False,configuration=config)

            reponse = make_response(pdf)
            reponse.headers['Content-Type'] ='application/pdf'
            reponse.headers['Content-Disposition'] = 'attachment; filename=myreport.pdf'
            return reponse