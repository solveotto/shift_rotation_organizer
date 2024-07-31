from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import json


app = Flask(__name__)
app.secret_key = "secret"


class DataframeManager():
    def __init__(self) -> None:
        self.df = pd.read_json('turnus_df_R24.json')
        self.helgetimer_mulip = 1
        self.ettermiddager = 0
        self.ettermiddag_poeng = 0

        self.update_df()

    def update_df(self):
        self.calc_helgetimer()
        self.calc_ettermiddag_vakter()
        #self.calc_netter()
        self.df = self.df.sort_values(by='poeng')


    def calc_helgetimer(self):
        self.df['poeng'] = self.df['poeng'] + self.df['helgetimer'] * self.helgetimer_mulip

    def calc_netter(self):
        self.df.loc[self.df['natt'] > 6, 'poeng'] += 1

    def calc_ettermiddag_vakter(self):
        threshold = self.ettermiddager  # Specific threshold
        multiplier = self.ettermiddag_poeng  # Amount to multiply

        # Iterate through each row in the DataFrame
        for index, row in self.df.iterrows():
            if row['ettermiddag'] > threshold:
                # Multiply the 'ettermiddag' value by the specified amount
                self.df.at[index, 'poeng'] += (row['ettermiddag'] - threshold) * multiplier


        

df_manager = DataframeManager()


@app.route('/')
def home():
    # Convert DataFrame to a list of dictionaries
    table_data = df_manager.df.to_dict(orient='records')

    helgetimer = session.get('helgetimer', '0')
    ettermiddager = session.get('ettermiddager', '0')
    ettermiddager_poeng = session.get('ettermiddager_poeng', '0')

   
    session.clear()

    # Pass the table data to the template
    return render_template('index.html', 
                           table_data = table_data, 
                           helgetimer = helgetimer,
                           ettermiddager = ettermiddager,
                           ettermiddager_poeng = ettermiddager_poeng
                           )


@app.route('/submit', methods=['POST'])
def calulate():
    # Resets points value
    df_manager.df['poeng'] = 0
   
    helgetimer = request.form.get('helgetimer', '0')
    df_manager.helgetimer_mulip = int(helgetimer)
    session['helgetimer'] = helgetimer

    ettermiddager = request.form.get('ettermiddager', '0')
    df_manager.ettermiddager = int(ettermiddager)
    session['ettermiddager'] = ettermiddager
    
    ettermiddager_poeng = request.form.get('ettermiddager_poeng', '0')
    df_manager.ettermiddag_poeng = int(ettermiddager_poeng)
    session['ettermiddager_poeng'] = ettermiddager_poeng
    
    
    
    df_manager.update_df()
    
    
    
    


    #return render_template('index.html', helgetimer=helgetimer)
    return redirect(url_for('home'))


@app.route('/search')
def search():
    return render_template('search.html')



if __name__ == '__main__':
    app.run(port=8080, debug=True)