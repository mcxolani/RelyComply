from flask import Flask, render_template, redirect, request, url_for
import threading
import time

app = Flask(__name__)

db = {}

start_data = {
    'accepted': None,
    'declined': None,
    'currentStep': None,
    'status': 'idle',
    'income': 0,
    'name': '',
    'surname': '',
    'dob': ''
}

sanctions = ['user-user', 'user-wow', 'joe-smith']
pep_list = ['user-user', 'user-wow', 'john-smith']

def start1(user_data):
    user_id = f"{user_data.get('name')}-{user_data.get('surname')}"
    db[user_id] = {**start_data, **user_data}
    db[user_id]['status'] = 'busy' 
    db[user_id]['currentStep'] = 'checkSanctions'
    threading.Thread(target=checkSanctions, args=(user_id, )).start()
    return user_id

def checkPep(user_id):
    db[user_id]['currentStep'] = 'checkPep'
    db[user_id]['status'] = 'busy'

    time.sleep(10)

    if user_id in pep_list:
        db[user_id]['currentStep'] = 'confrimPep'
        db[user_id]['status'] = 'idle'
    else:
        threading.Thread(target=riskAsses, args=(user_id, False)).start()

def checkSanctions(user_id):

    db[user_id]['currentStep'] = 'checkSanctions'
    db[user_id]['status'] = 'busy'

    time.sleep(10)
    
    if user_id in sanctions:
        db[user_id]['currentStep'] = 'confrimSanctions'
        db[user_id]['status'] = 'idle'
    else:
        threading.Thread(target=checkPep, args=(user_id, )).start()

def riskAsses(user_id, match):
    db[user_id]['currentStep'] = 'riskAsses'
    db[user_id]['status'] = 'busy'

    user = db.get(user_id)
    time.sleep(10)
    if not match:
        db[user_id]['currentStep'] = 'finished'
        db[user_id]['status'] = 'done'
        db[user_id]['accepted'] = True
    elif  int(user.get('income')) < 25000:
        db[user_id]['currentStep'] = 'finished'
        db[user_id]['status'] = 'done'
        db[user_id]['declined'] = True
    else:
        db[user_id]['currentStep'] = 'finished'
        db[user_id]['status'] = 'done'
        db[user_id]['accepted'] = True


def handleUserAction(user_id, action=None):

    if action is None:
        return

    if action == "no_match_pep":
        threading.Thread(target=riskAsses, args=(user_id, False)).start()
        return

    if action == "yes_match_pep":
        threading.Thread(target=riskAsses, args=(user_id, True)).start()
        return

    if action == "yes_match_senctions":
        db[user_id]['declined'] = True
        return

    if action == "no_match_senctions":
        threading.Thread(target=checkPep, args=(user_id, )).start()
        return


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = start1(request.form)
        return redirect(url_for('user', user_id = user_id))

    return f"""
        <form method="post">
            <div>
                <label for="name">name</label>
                <input name="name" id="name" required />
            </div>

            <div>
                <label for="surname">surname</label>
                <input name="surname" id="surname" required />
            </div>

            <div>
                <label for="dob">Date Of Birth</label>
                <input name="dob" id="dob" required />
            </div>

            <div>
                <label for="income">income</label>
                <input name="income" id="income" required />
            </div>

            <div>
                <input type="submit" value="Register" />
            </div>
        </form>"""

@app.route("/<user_id>", methods=['GET', 'POST'])
def user(user_id):
    if request.method == 'POST':
        handleUserAction(user_id, request.form['action'])

    user = db.get(user_id)

    if user.get('declined'):
        return f"""
            <h1>Declined Sorry Bye</p>
        """

    if user.get('accepted'):
        return f"""
            <h1>Welcome to the bank, your detailes are {str(user)}</p>
        """

    if user.get('status') == 'busy':
        return f"""
            <h1>Loading... we busy with: {user.get('currentStep')} action</p>
        """

    if user.get('status') == 'idle':
        if user.get('currentStep') == 'confrimPep':
            return f"""
                <h1>We found User on PEP List, Please confirm?</h1>
                <form method="post">
                    <input type="hidden" name="action" value="yes_match_pep" />
                    <div>
                        <input type="submit" value="Yes" />
                    </div>
                </form>

                <form method="post">
                    <input type="hidden" name="action" value="no_match_pep" />
                    <div>
                        <input type="submit" value="No" />
                    </div>
                </form>
            """
        if user.get('currentStep') == 'confrimSanctions':
            return f"""
                <h1>We found User on Senctions list, Please confirm is it the right user?</h1>
                <form method="post">
                    <input type="hidden" name="action" value="yes_match_senctions" />
                    <div>
                        <input type="submit" value="Yes" />
                    </div>
                </form>

                <form method="post">
                    <input type="hidden" name="action" value="no_match_senctions" />
                    <div>
                        <input type="submit" value="No" />
                    </div>
                </form>
            """

        return f"""
            <h1>We just idle for nothing</p>
        """


    return f"""
    
            <p>Hello, World! {str(db.get(user_id))}</p>
    
            <h1>We found User on Section, Please confirm is it the right user?</h1>
            <form method="post">
                <input type="hidden" name="action" value="yes_match_senctions" />
                <div>
                    <input type="submit" value="Yes" />
                </div>
            </form>

            <form method="post">
                <input type="hidden" name="action" value="no_match_senctions" />
                <div>
                    <input type="submit" value="No" />
                </div>
            </form>
    """