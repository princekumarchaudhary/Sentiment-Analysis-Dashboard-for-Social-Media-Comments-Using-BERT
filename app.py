from flask import Flask, render_template, request, redirect, url_for, session
# from scripts import main_dashboard
import main_dashboard
import json
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from statistics import mean

app = Flask(__name__)

app.secret_key = 'xyzsdfg'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'demo'

mysql = MySQL(app)



@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('twitter.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
 

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('login.html', mesage = mesage)

# @app.route('/index.html')
# @app.route('/home')
# def home():
#     return render_template("index.html")



@app.route('/twitter.html')
def twitter():
    return render_template("twitter.html")

@app.route('/result',methods=['POST', 'GET'])
def result():
    output = request.form.to_dict()
    link = output["name"]
    total_avg_result,world_map_avg_score, cur_comment_data, avg_data_info, comments_data = main_dashboard.tweet_analysis(link)
    rv = total_avg_result[0]
    if rv == -1:
        rv = 'no result' 
    avg_data_labels = []
    avg_data_values = []
    scaling=[10,100,1000,10000]
    for key,value in avg_data_info.items():
        avg_data_labels.append(key)
        avg_data_values.append(value) 


    world_map_avg_score_labels = []
    world_map_avg_score_sentiment = []
    world_map_avg_score_variance = []
    for key,value in world_map_avg_score.items():
        world_map_avg_score_labels.append(key)
        for i in value:
            if(i=='sentiment_list'):
                world_map_avg_score_sentiment.append(value[i])
            elif (i=='variance_list'):
                world_map_avg_score_variance.append(value[i])


    cur_comment_data_dict = cur_comment_data[0]  
    cur_comment_data_values = []
    cur_comment_data_values.append(cur_comment_data_dict["favorite_count"])  
    cur_comment_data_values.append(cur_comment_data_dict["retweet_count"])
    cur_comment_data_values.append(cur_comment_data[1])
    cur_comment_data_values.append(cur_comment_data[2])  

    for i in range(len(avg_data_values)):
        avg_data_values[i] = round(float(avg_data_values[i]),1)

    for i in range(len(cur_comment_data_values)):
        cur_comment_data_values[i] = round(float(cur_comment_data_values[i]),1)

    print("Average Comments data")
    print(avg_data_values)
    print("Current Comment Data")
    print(cur_comment_data_values) 

    max_val = max(avg_data_values)       
    max_val_cur = max(cur_comment_data_values)
    final_max = max(max_val,max_val_cur)
 

    sf1 = len(str(final_max)) - len(str(max(avg_data_values[0],cur_comment_data_values[0])))
    scaling_factor1 = pow(10,sf1)
    print("scaling_factor1")
    print(scaling_factor1)

    sf2 = len(str(final_max)) - len(str(max(avg_data_values[1],cur_comment_data_values[1])))
    scaling_factor2 = pow(10,sf2)
    print("scaling_factor2")
    print(scaling_factor2)

    sf3 = len(str(final_max)) - len(str(max(avg_data_values[2],cur_comment_data_values[2])))
    scaling_factor3 = pow(10,sf3)
    print("scaling_factor3")
    print(scaling_factor3)

    # sf4 = len(str(final_max)) - len(str(round(max(avg_data_values[3],cur_comment_data_values[3]),2)))
    scaling_factor4 = pow(10,sf3)
    print("scaling_factor4")
    print(scaling_factor4)

    # This is for avg data
    avg_data_values[0] = avg_data_values[0]*scaling_factor1
    avg_data_values[1] = avg_data_values[1]*scaling_factor2
    avg_data_values[2] = avg_data_values[2]*scaling_factor3
    avg_data_values[3] = avg_data_values[3]*scaling_factor4

#    This is for current data
    cur_comment_data_values[0] = cur_comment_data_values[0]*scaling_factor1
    cur_comment_data_values[1] = cur_comment_data_values[1]*scaling_factor2
    cur_comment_data_values[2] = cur_comment_data_values[2]*scaling_factor3
    cur_comment_data_values[3] = cur_comment_data_values[3]*scaling_factor4 

#   This is for comments Data
    line_labels=[]
    line_favorit_counts=[]
    line_retweet_counts=[]
    line_sentiment_scores=[]
    line_variance_scores=[]
    for i in range(len(comments_data)):
        comment = comments_data[i]
        line_labels.append(comment["created_at"])
        line_favorit_counts.append(comment["favorite_count"])
        line_retweet_counts.append(comment["retweet_count"])
        line_sentiment_scores.append(comment["sentiment_score"])
        line_variance_scores.append(comment["variance_score"])

    line_max2 = len(str(max(max(line_favorit_counts),max(line_retweet_counts)))) - len(str(max(line_sentiment_scores)))
    sff2 = pow(10,len(str(line_max2))+2)

    # line_max3 = len(str(max(max(line_favorit_counts),max(line_retweet_counts)))) - len(str(max(line_variance_scores)))
    sff3 = pow(10,len(str(line_max2))+2)

    print("sff2 : ")
    print(sff2)
    print("sff3 : ")
    print(sff3)

    print("line_sentiment_scores_old")
    print(line_sentiment_scores)
    print("line_variance_scores_old")
    print(line_variance_scores)
    print("line_favorit_counts_old")
    print(line_favorit_counts)
    print("line_retweet_counts_old")
    print(line_retweet_counts)

    for i in range(len(line_sentiment_scores)): 
        line_sentiment_scores[i] = line_sentiment_scores[i]*sff2
    for i in range(len(line_variance_scores)): 
        line_variance_scores[i] = line_variance_scores[i]*sff3
    
    print("line_sentiment_scores_new")
    print(line_sentiment_scores)
    print("line_variance_scores_new")
    print(line_variance_scores)
    print("line_favorit_counts_new")
    print(line_favorit_counts)
    print("line_retweet_counts_new")
    print(line_retweet_counts)
    
    # print("world_map_avg_score_labels")
    # print(world_map_avg_score_labels)
    # print("world_map_avg_score_sentiment")
    # print(world_map_avg_score_sentiment)
    # print("world_map_avg_score_variance")
    # print(world_map_avg_score_variance)  
    print("current_comment_data")
    print(cur_comment_data_values)
    print("avg_data_values")
    print(avg_data_values)

    return render_template('twitterchart.html', name=json.dumps(total_avg_result), score=rv,radar_label=json.dumps(avg_data_labels),
                            radar_current_value = json.dumps(cur_comment_data_values),radar_avg_value = json.dumps(avg_data_values),
                            line_label=json.dumps(line_labels),line_favorit_count=json.dumps(line_favorit_counts),line_retweet_count=json.dumps(line_retweet_counts),
                            line_sentiment_score=json.dumps(line_sentiment_scores),line_variance_score=json.dumps(line_variance_scores),
                            polar_label=json.dumps(world_map_avg_score_labels),polar_sentiment_score=json.dumps(world_map_avg_score_sentiment),polar_variance_score=json.dumps(world_map_avg_score_variance))

@app.route('/barchart')
def bar():
    return render_template('sentiment.html',name=json.dumps(sentiment))

@app.route('/radarchart')
def radar():
    return render_template('radar.html')

@app.route('/linechart')
def line():
    return render_template('line.html')

@app.route('/polarchartvar')
def polarvar():
    return render_template('polarchartvar.html')

@app.route('/polarchartsent')
def polarsent():
    return render_template('polarchartsent.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
    
if __name__ == "__main__":
    app.run(debug=True)