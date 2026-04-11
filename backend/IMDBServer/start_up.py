import pymongo
import json
from flask import Flask,request,jsonify
import pprint

import ssl, smtplib, mimetypes

from email.message import EmailMessage


connection_str='mongodb://localhost:27017/'
_mongo_client=pymongo.MongoClient(connection_str)

print(_mongo_client)

# my_db=_mongo_client['new_db_one']
# my_col=my_db['new_col']
app=Flask(__name__)
# def auto_emailer(_body,_sub):
#     _context=ssl.create_default_context()
#     _host='smtp.gmail.com'
#     _port=587
#     _user='anirudh07072003@gmail.com'
#     with smtplib.SMTP(host=_host,port=_port) as _server:
#         _server.starttls(context=_context)
#         _server.login(_user,'fgpl nyno sjsm avdg')
#         _server.sendmail("anirudh07072003@gmail.com", \
#                         to_addrs='anirudh07072003@gmail.com', \
#                         msg="""subject : || {_sub}  ||
#                         \n \n {_body} \n Thank you""")
#         attachment_path = "requirements.txt"
#         if attachment_path:
#             try:
#                 mime_type, _ = mimetypes.guess_type(attachment_path)
#                 mime_type, mime_subtype = (
#                 mime_type.split("/") if mime_type else ("application", "octet-stream")
#             )

#             with open(attachment_path, "rb") as file:
#                 email.add_attachment(
#                     file.read(),
#                     maintype=mime_type,
#                     subtype=mime_subtype,
#                     filename=attachment_path.split("/")[-1],
#                 )
#             except Exception as e:
#                 print(f"Attachment error: {e}")


# auto_emailer('test','body')



def auto_emailer(sub, msg):
    _context = ssl.create_default_context()
    _host = "smtp.gmail.com"
    _port = 587
    _user = "anirudh07072003@gmail.com"
    email = EmailMessage()
    email["From"] = _user
    email["To"] = "vakalohithreddy2014@gmail.com"
    email["Subject"] = sub
    email.set_content(f"{msg}\n\nThank you")
    attachment_path = "imdb_data.json"
    if attachment_path:
        try:
            mime_type, _ = mimetypes.guess_type(attachment_path)
            mime_type, mime_subtype = (
                mime_type.split("/") if mime_type else ("application", "octet-stream")
            )

            with open(attachment_path, "rb") as file:
                email.add_attachment(
                    file.read(),
                    maintype=mime_type,
                    subtype=mime_subtype,
                    filename=attachment_path.split("/")[-1],
                )
        except Exception as e:
            print(f"Attachment error: {e}")
    with smtplib.SMTP(host=_host, port=_port) as s:
        s.starttls(context=_context)
        s.login(_user, "fgpl nyno sjsm avdg")
        # s.sendmail(
        #     _user,
        #     to_addrs="ganeshganeshsanagala@gmail.com",
        #     msg=f"""Subject: {sub} \n\n {msg} \n Thankyou""",
        # )
        s.send_message(email)
# Remove or guard the auto_emailer test call
# auto_emailer("hi ra  ", "po ra ")

@app.route('/insert_data_into_database/' ,methods=['PUT'])

def insert_data_into_database():
    _data=request.json
    if _data is None:
        return jsonify({'error': 'No JSON data provided'}), 400
    filtered_data=[]
    for _rec in _data:
        _rec.update({'_id':{'oid':_rec['_id']['$oid']}})
        filtered_data.append(_rec)
    pprint.pprint(filtered_data)
    # with open('imdb_data.json',mode='r') as f:
    #     _data=json.load(f)
    # print(_data)
    # imdb_db=_mongo_client['imdb_storage']
    # imdb_col=imdb_db['imdb_collection']
    imdb_db=_mongo_client['imdb_db']
    imdb_col=imdb_db['imdb_collection']
    # imdb_col.insert_many(_data)
    _status=imdb_col.insert_many(filtered_data)
    return jsonify({'status':str(_status)})

@app.route('/top_director_with_maximum_number_of_movie/' ,methods=['GET'])
def top_director_with_maximum_number_of_movie():
    _data=_mongo_client['imdb_db']['imdb_collection'].find()
    bolist=[]
    total = []
    for entry in _data:
        if "box_office_million_usd" in entry:
            bolist.append(entry)
    print(bolist)    
    low=[]
    med=[]
    high=[]
    for entry in bolist:
        bo=entry['box_office_million_usd']
        score=entry['imdb_score']
        if bo<100:
            low.append(score)
        elif bo>500:
            high.append(score)
        else:
            med.append(score)
    auto_emailer("the avg of imdb score of movies with box office <100M",f'{sum(low)/len(low)}')
    return jsonify({"avg_imdb_score_box_office_lt_100M": sum(low)/len(low)})
    # print(f"the avg of imdb score of movies with box office >100M and >500M {sum(med)/len(med)}")           
    # print(f"the avg of imdb score of movies with box office >500M {sum(high)/len(high)}")                  

@app.route('/Director_Success_Analysis/' ,methods=['GET'])
def Director_Success_Analysis():
    _data=_mongo_client['imdb_db']['imdb_collection'].find()
    dc={}
    for entry in _data:
        director = entry["director"]
        if director in dc:
            dc[director] += 1
        else:
            dc[director] = 1
    l=[]
    for key in dc:
        if dc[key] >= 3:
            l.append(key)
    print(l)
    score_dict={}
    bo_dict={}
    for entry in _mongo_client['imdb_db']['imdb_collection'].find():
        direc=entry['director']
        if direc in l:
                if direc not in score_dict:
                    score_dict[direc] = entry['imdb_score']
                else:
                    score_dict[direc] += entry['imdb_score']
    for key in score_dict:
        score_dict[key]=score_dict[key]/dc[key]
    for entry in _mongo_client['imdb_db']['imdb_collection'].find():
        direc=entry['director']
        if direc in l:
                if direc not in bo_dict:
                    if entry.get('box_office_million_usd') != None :
                        bo_dict[direc] = entry.get('box_office_million_usd')
                    else:
                        bo_dict[direc] =0
                else:
                    if entry.get('box_office_million_usd') != None :
                        bo_dict[direc] += entry.get('box_office_million_usd')
                    else:
                        bo_dict[direc] += 0
    return jsonify(bo_dict)

@app.route('/analyze_scores_by_decade/' ,methods=['GET'])
def analyze_scores_by_decade():
    _data=_mongo_client['imdb_db']['imdb_collection'].find()
    y_dict={}
    l=[]
    for entry in _data:
        rd=entry.get('release_date')
        if rd:
            l.append(int(rd[0:4]))
    _data=_mongo_client['imdb_db']['imdb_collection'].find()  # re-fetch cursor
    for entry in _data:
        rd=entry.get('release_date')
        if rd:
            y_dict[int(rd[0:4])]=entry['imdb_score']
    # Initialize y with float values
    y={1970:0.0,1980:0.0,1990:0.0,2000:0.0,2010:0.0,2020:0.0}
    for key in y_dict:
        if (key >=1970 and key <= 1980):
            y[1970]+=y_dict[key]
        elif (key >=1980 and key <= 1990):
            y[1980]+=y_dict[key]
        elif (key >=1990 and key <= 2000):
            y[1990]+=y_dict[key]
        elif (key >=2000 and key <= 2010):
            y[2000]+=y_dict[key]
        elif (key >=2010 and key <= 2020):
            y[2010]+=y_dict[key]
        else:
            y[2020]+=y_dict[key]
    y_70=0
    y_80=0
    y_90=0
    y_00=0
    y_10=0
    y_20=0
    for key in y_dict:
        if (key >=1970 and key <= 1980):
            y_70+=1
        elif (key >=1980 and key <= 1990):
            y_80+=1
        elif (key >=1990 and key <= 2000):
            y_90+=1
        elif (key >=2000 and key <= 2010):
            y_00+=1
        elif (key >=2010 and key <= 2020):
            y_10+=1
        else:
            y_20+=1
    y[1970]=y[1970]/y_70 if y_70 else 0.0
    y[1980]=y[1980]/y_80 if y_80 else 0.0
    y[1990]=y[1990]/y_90 if y_90 else 0.0
    y[2000]=y[2000]/y_00 if y_00 else 0.0
    y[2010]=y[2010]/y_10 if y_10 else 0.0
    y[2020]=y[2020]/y_20 if y_20 else 0.0
    return jsonify(y)
    
@app.route('/find_top_movies_by_language/' ,methods=['GET'])
def find_top_movies_by_language():
    _data=_mongo_client['imdb_db']['imdb_collection'].find()   
    l=[]
    for entry in _data:
        lan=entry.get('language')
        if lan :
            l.append(lan)
    lan_list=list(set(l))
    l_dict={ key:[] for key in lan_list}
    _data=_mongo_client['imdb_db']['imdb_collection'].find()  # re-fetch cursor
    for entry in _data:
        lan=entry.get('language')
        name=entry.get('name')
        score=entry.get('imdb_score')
        if lan and name and isinstance(score, (int, float)):
                l_dict[lan].append((name, score))
    top_movies = {}
    for lang, movie_list in l_dict.items():
            sorted_movies = sorted(movie_list, key=lambda x: x[1], reverse=True)
            top_movies[lang] = sorted_movies[:10]
    return jsonify(top_movies)    


@app.route('/analyze_awards_vs_scores/' ,methods=['GET'])
def analyze_awards_vs_scores():
    _data=_mongo_client['imdb_db']['imdb_collection'].find() 
    groups = {
            '0': [],
            '1-3': [],
            '4-6': [],
            '7+': []
        }

    for entry in _data:
            awards = entry.get('awards_won')
            score = entry.get('imdb_score')

            if awards is not None and score is not None:
                if awards == 0:
                    groups['0'].append(score)
                elif 1 <= awards <= 3:
                    groups['1-3'].append(score)
                elif 4 <= awards <= 6:
                    groups['4-6'].append(score)
                else:  
                    groups['7+'].append(score)


    avg_scores = {}
    for group, scores in groups.items():
            if scores:
                avg_scores[group] = sum(scores) / len(scores)
            else:
                avg_scores[group] = None  
    return jsonify(avg_scores)

@app.route('/analyze_runtime_statistic/' ,methods=['GET'])
def analyze_runtime_statistics():
    _data=_mongo_client['imdb_db']['imdb_collection'].find() 
    rt_list=[]
    for entry in _data:
        rt=entry.get('runtime_minutes')
        if rt and rt>0:
            rt_list.append(rt)
        
    #print(rt_list)
    stats={}
    stats['min'] = min(rt_list) if rt_list else None
    stats['max'] = max(rt_list) if rt_list else None
    stats['average'] = sum(rt_list) / len(rt_list) if rt_list else None
    #print(stats)
    categories = {'short': 0, 'medium': 0, 'long': 0}

    for i in rt_list:
            if i < 90:
                categories['short'] += 1
            elif 90 <= i <= 150:
                categories['medium'] += 1
            else:
                categories['long'] += 1
    return jsonify({"stats": stats, "categories": categories})

@app.route('/analyze_language_distribution/' ,methods=['GET'])
def analyze_language_distribution():
    _data=list(_mongo_client['imdb_db']['imdb_collection'].find())
    d={}
    for entry in _data:
        lan=entry.get('language')
        if lan:
            if lan not in d:
                d[lan]=1
            else:
                d[lan]+=1
    # print(d)
    # print(len(j))
    for key in d:
        d[key]=(d[key]/len(_data))*100 if len(_data) else 0
    return jsonify(d)

   
if __name__=='__main__':
    app.run(port=5000,debug=True)
        