from flask import Flask, render_template, request, abort, redirect
import string
import secrets
import sqlite3
class DataBase:
    def __init__(self, filename):
        self.filename=filename
        con = sqlite3.connect(filename)
        c= con.cursor()
        try:
            c.execute('''
            CREATE TABLE IF NOT EXISTS links(
                code TEXT PRIMARY KEY,
                link TEXT
            );
            ''')
        finally:
            con.close()    
    def add_link(self, code, link):
        con=sqlite3.connect(self.filename)
        c=con.cursor()
        try:
            c.execute('''INSERT INTO links (code, link) VALUES (?, ?)''', (code, link,))    
            con.commit()
            return True
        except sqlite3.IntegrityError:  
            return False
        finally:
            con.close()
    def get_link(self,code):
        con=sqlite3.connect(self.filename)
        c=con.cursor()
        try:
            c.execute('''SELECT link FROM links WHERE code = ?''',(code,))    
            unrow = c.fetchone()
        finally:
            con.close()
        if not unrow is None: 
            return unrow[0]
        else:
            return None     
app = Flask(__name__)
c=DataBase('links.db')
def make_code():
    partsOfCode=[]
    stringed= string.ascii_letters + string.digits
    for i in range(6):
        partsOfCode.append(secrets.choice(stringed))
    gotted = ''.join(partsOfCode)
    return gotted    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        answer = request.form['link'].strip()
        if answer.startswith(('https://', 'http://')):
            for _ in range(5):
                code = make_code()
                if c.add_link(code, answer) is True:
                    return render_template('result.html', short =request.host_url+code)
            else:
                return f'not completed, please try again'
        else:
            return 'The link must begin with https:// or http://'
    return render_template('index.html')
@app.route('/<code>')
def redirectUser(code):
    link=c.get_link(code)
    if link is None:
        abort(404)
    return redirect(link)    
if __name__ == '__main__':
    app.run(debug=True)