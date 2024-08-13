from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import json



app = Flask(__name__)
app.secret_key = "secret"


class DataframeManager():
    def __init__(self) -> None:
        self.df = pd.read_json('turnus_df_R24.json')
        self.helgetimer_dagtid_multip = 0

        self.sort_by_input = 'Navn'
        self.sort_by_ascending = True



    def sort_by(self, _type, ascending=True):

        if _type == 'turnus':
            sort_name = 'Navn'
        else:
            sort_name = _type.replace("_", " ")

        self.sort_by_input = sort_name.title()
        self.df = self.df.sort_values(by=_type, ascending=ascending)


    def calc_multipliers(self, _type, multip):
        self.df['poeng'] = round(self.df['poeng'] + self.df[_type] * multip, 1)
        #self.df['poeng'] = round(self.df['poeng'] + self.df['helgetimer_dagtid'] * multip, 1)

    def calc_thresholds(self, _type, _th, multip):
        for index, row in self.df.iterrows():
            if row[_type] > _th:
                self.df.at[index, 'poeng'] += (row[_type] - _th) * multip

class TurnusManager():
    def __init__(self) -> None:
        with open('turnuser_R24.json', 'r') as f:
            self.data = json.load(f)
        
  
df_manager = DataframeManager()
turnus_mangaer = TurnusManager()


@app.route('/')
def home():
    # Convert DataFrame to a list of dictionaries
    ## table_data = df_manager.df.to_dict(orient='records')

    # Gets the values set by the user 
    helgetimer = session.get('helgetimer', '0')
    helgetimer_dagtid = session.get('helgetimer_dagtid', '0')
    ettermiddager = session.get('ettermiddager', '0')
    ettermiddager_poeng = session.get('ettermiddager_poeng', '0')
    nights = session.get('nights', '0')
    nights_pts = session.get('nights_pts', '0')


    sort_btn_name = df_manager.sort_by_input

     # Pass the table data to the template
    return render_template('index.html', 
                           table_data = df_manager.df.to_dict(orient='records'), 
                           helgetimer = helgetimer,
                           helgetimer_dagtid = helgetimer_dagtid,
                           ettermiddager = ettermiddager,
                           ettermiddager_poeng = ettermiddager_poeng,
                           nights = nights,
                           nights_pts = nights_pts,
                           sort_by_btn_name = sort_btn_name
                           )


@app.route('/submit', methods=['POST'])
def calculate():
    # Resets points value
    df_manager.df['poeng'] = 0
    df_manager.sort_by('turnus')
   
    helgetimer = request.form.get('helgetimer', '0')
    df_manager.calc_multipliers('helgetimer', float(helgetimer))
    session['helgetimer'] = helgetimer
    
    helgetimer_dagtid = request.form.get('helgetimer_dagtid', '0')
    df_manager.calc_multipliers('helgetimer_dagtid', float(helgetimer_dagtid))
    session['helgetimer_dagtid'] = helgetimer_dagtid

    # calculate points for ettermiddager
    ettermiddager = request.form.get('ettermiddager', '0')
    ettermiddager_pts = request.form.get('ettermiddager_poeng', '0')
    session['ettermiddager'] = ettermiddager
    session['ettermiddager_poeng'] = ettermiddager_pts
    df_manager.calc_thresholds('ettermiddag', int(ettermiddager), int(ettermiddager_pts))
    

    # caluclate points for nights
    nights = request.form.get('nights', '0')
    nights_pts = request.form.get('nights_pts')
    session['nights'] = nights
    session['nights_pts'] = nights_pts
    df_manager.calc_thresholds('natt', int(nights), int(nights_pts))
    
    
    
    df_manager.sort_by('poeng', True)
    
    
    
    


    #return render_template('index.html', helgetimer=helgetimer)
    return redirect(url_for('home'))

@app.route('/sort_by_column')
def sort_by_column():

    column = request.args.get('column')
    if column in df_manager.df:
        df_manager.sort_by(column)
    else:
        df_manager.sort_by('poeng')
        

    
    return redirect(url_for('home'))

@app.route('/reset')
def reset():
    session.clear()
    df_manager.df['poeng'] = 0
    df_manager.sort_by('turnus')
    

    return redirect(url_for('home'))





@app.route('/api/receive-data', methods=['POST'])
def receive_data():
    html_data = request.get_json()
    selected_shift = html_data.get('turnus')
    
    for x in turnus_mangaer.data:
        for shift_name, shift_data in x.items():
            if shift_name == selected_shift:
                print(json.dumps(shift_data, indent=4))
                session['shift_name'] = shift_name
                session['shift_data'] = shift_data
                break
                
    return redirect(url_for('display_shift'))

@app.route('/display_shift')
def display_shift():
    shift_name = session.get('shift_name')
    shift_data = session.get('shift_data')
    

    if shift_name and shift_data:
        print('test')
        return render_template('turnus.html', shift_name=shift_name, shift_data=shift_data)
    else:
        return "No shift data found", 400


if __name__ == '__main__':
    app.run(port=8080, debug=True)