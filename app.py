from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import json


app = Flask(__name__)
app.secret_key = "secret"


class DataframeManager():
    def __init__(self) -> None:
        self.df = pd.read_json('turnus_df_R24.json')
        self.helgetimer_mulip = 1

        self.update_df()

    def update_df(self):
        self.calc_helgetimer()
        self.calc_netter()


    def calc_helgetimer(self):
        self.df['poeng'] = self.df['poeng'] + self.df['helgetimer'] * self.helgetimer_mulip

    def calc_netter(self):
        self.df.loc[self.df['natt'] > 6, 'poeng'] += 1


        

df_manager = DataframeManager()


@app.route('/')
def home():
    # Convert DataFrame to a list of dictionaries
    table_data = df_manager.df.to_dict(orient='records')

    helgetimer = session.get('helgetimer', '0')

    session.clear()

    # Pass the table data to the template
    return render_template('index.html', table_data=table_data, helgetimer=helgetimer)


@app.route('/submit', methods=['POST'])
def calulate():
    # Resets points value
    df_manager.df['poeng'] = 0
   
    helgetimer = request.form.get('helgetimer', '0')
    df_manager.helgetimer_mulip = int(helgetimer)

    
    
    
    df_manager.update_df()
    
    session['helgetimer'] = helgetimer
    
    
    


    #return render_template('index.html', helgetimer=helgetimer)
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(port=8080, debug=True)