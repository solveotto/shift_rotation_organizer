from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import json


app = Flask(__name__)
app.secret_key = "secret"



org_df = pd.read_json('turnus_df_R24.json')


    



@app.route('/')
def home():
    session['dataframe'] = org_df.to_json(orient='split')
    df_json = session.get('dataframe')
    df = pd.read_json(df_json, orient='split')
    
    #data = df.to_html()

    # Convert DataFrame to a list of dictionaries
    table_data = df.to_dict(orient='records')

    # Pass the table data to the template
    return render_template('index.html', table_data=table_data)


@app.route('/submit', methods=['POST'])
def calulate():
    df_json = session.get('dataframe')
    df_calc = pd.read_json(df_json, orient='split')
    print(type(df_calc))



    helgetimer_input = int(request.form['helgetimer'])

    df_calc['poeng'] = df_calc['poeng'] + df_calc['helgetimer']

    
    
    #df_calc = session.get('dataframe')

    
    #df_calc.loc[df_calc['natt'] > 6, 'poeng'] += 1

    session['dataframe'] = df_calc.to_json(orient='split')


    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(port=8080, debug=True)