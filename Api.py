from flask import Blueprint,render_template,request,redirect,url_for,session,jsonify
import pymysql
from config import *
con = pymysql.connect(HOST,USER,PASS,DATABASE)
memberapi = Blueprint('memberapi',__name__)
@memberapi.route("/api/memberapi",methods=["POST","GET"])
def Memberapi():
    with con:
        cur = con.cursor()
        sql = "select mem_id,mem_fname,mem_lname,mem_sex from tb_member"
        cur.execute(sql)
        rows = cur.fetchall()
        mydata = []
        for i in range(len(rows)):
            task = {
                'id':i,
                'mem_id':rows[i][0],
                'mem_fname':rows[i][1],
                'mem_lname':rows[i][2],
                'mem_sex':rows[i][3],
            }
            mydata.append(task) 
        return jsonify(mydata,201,{'Content-Type': "application/json"})