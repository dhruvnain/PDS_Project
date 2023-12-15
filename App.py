from flask import Flask, render_template, request, redirect, session, jsonify,flash, redirect
from helper.sql_helper import query_db,insert_db,delete_from_db,drop_table
import re,ast
import json
import helper.sql_query as sq
app = Flask(__name__)
app.secret_key = 'this_is_a_secret_key'
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/logout', methods=['POST'])  
def logout():
    # Your logout logic here
    # Invalidate the user session
    # ...

    # Redirect to the login page or return a success response
    return redirect('/login')   # or return a success status


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        print("U",type(username))
        password = request.form['password']
        if (len(username) != 0):
            # Adjust the query to check if the user exists with the given username and password
            user = query_db(sq.query1, [username], one=True)
            passw = query_db(sq.query2, [password], one=True)
            
            if user and passw:
                # User found, render dashboard
                userid = query_db(sq.query3,[username],one = True)
                #return render_template('dashboard.html')
                return options(userid)
            else:
                # User not found, show error message
                print('Invalid username or password')  # This requires setting up Flask's flash messaging
                flash('Invalid username or password', 'error')
                return redirect('/login') 
        else:
            flash('Invalid username or password', 'error')
            return redirect('/login')

    else:
        return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
    # Placeholder for actual registration logic
    # Assuming you get the username from the form
        username = request.form['username']
        password = request.form['password']
        if (len(username) != 0 and len(password)!=0):
            user = query_db(sq.query1, [username], one=True)
            if user:
                # User already exists
                flash('Username already exists') 
                print('Username already exists')
                return redirect('/login') 
            else:
                first_name = request.form['first_name']
                last_name = request.form['last_name']
                d = query_db(sq.query4, [], one=True)
                if d[0] is not None:  # Check if the result is not None
                    id = int(d[0])  # Convert the first element of the tuple to int
                else:
                    id = 1  # Start from 1 if there are no entries
                id += 1  # Increment the id
                # User not found, insert into table
                user = insert_db(sq.query5, (id, first_name, last_name, username, password))
                return options(id)
        else:
            flash('Cannot enter with the above Username') 
            return redirect('/login') 
    return render_template('register.html')

@app.route('/home/<username>',methods=['GET','POST'])
def back_home(username):
    userid= query_db(sq.query3,[username],one = True)
    return options(userid[0])


@app.route('/options/<username>',methods=['GET','POST'])
def options(id):
    username = query_db(sq.query6,[id],one = True)
    return render_template('options.html', username=username[0])


@app.route('/add_service_location/<username>', methods=[ 'POST'])
def add_service(username):
    return render_template('add_service_location.html', username=username)

@app.route('/submit-address/<username>', methods=['POST'])
def submit_address(username):
    unitnumber = request.form.get('unitnumber')
    startdate = request.form.get('startdate')
    squarefootage = request.form.get('squarefootage')
    bedrooms = request.form.get('bedrooms')
    occupantnumber = request.form.get('occupantnumber')
    addressline1 = request.form.get('addressline1')
    addressline2 = request.form.get('addressline2')
    city = request.form.get('city')
    state = request.form.get('state')
    zipcode = request.form.get('zipcode')
    country = request.form.get('country')
    isBilling = request.form.get('isBilling') == 'on'
    a = query_db(sq.query7, [], one=True)
    if a[0] is not None:  # Check if the result is not None
        id = int(a[0])  # Convert the first element of the tuple to int
    else:
        id = 1  # Start from 1 if there are no entries
    id += 1  # Increment the id
    l = query_db(sq.query8, [], one=True)
    if l[0] is not None:  # Check if the result is not None
        locationid = int(a[0])  # Convert the first element of the tuple to int
    else:
        locationid = 1  # Start from 1 if there are no entries
    locationid += 1  # Increment the id
    customerid = query_db(sq.query3,[username],one = True)
    user_4=query_db(sq.query9,[addressline1, addressline2, city,state,country,zipcode])
    if (user_4[0][0]!=0):
        print("This location already exists")
        flash('Address already exists ')
        print("ok")
        return render_template('options.html', username=username)
    else:
        insert_db(sq.query10,(id, addressline1, addressline2, city,state,country,zipcode, isBilling))
        insert_db(sq.query11,(locationid,customerid,id,unitnumber,startdate,squarefootage,bedrooms,occupantnumber))

    # If isBilling is False, get the additional billing address fields
    if not isBilling:
        billingAddressline1 = request.form.get('billingAddressline1')
        billingAddressline2 = request.form.get('billingAddressline2')
        billingCity = request.form.get('billingCity')
        billingState = request.form.get('billingState')
        billingZipcode = request.form.get('billingZipcode')
        billingCountry = request.form.get('billingCountry')
        user_3=query_db(sq.query12,[billingAddressline1 ,billingAddressline2,billingCity ,billingState,billingCountry,billingZipcode])
        if (user_3[0][0]!=0):
            print("this billing address already exists")
            flash('Billing Address already exists')
            return render_template('options.html', username=username)
        else:
            id=id+1
            insert_db(sq.query13,[id,billingAddressline1 ,billingAddressline2,billingCity ,billingState,billingCountry,billingZipcode,'true'])
    # Redirect to another page or return a response
    print("not ok")
    return render_template('options.html', username=username)

@app.route('/delete_service_location/<username>', methods=['GET', 'POST'])
def delete_location(username):
    # Fetch locations for the given username
    query_1=query_db(sq.query3,[username])
    query_2=query_db(sq.query14,[query_1[0][0]])
    user_locations=[]
    for i in query_2:
        query_3=query_db(sq.query15,[i[0]])
        cleaned_str = re.sub(r'[^\w\s,]', '', query_3[0][0])
        cleaned_str = cleaned_str.replace(',', ' ')
        cleaned_str = ' '.join(cleaned_str.split())
        user_locations.append(cleaned_str)
    print(user_locations)
    return render_template('delete_service_location.html', serviceLocations=user_locations, username=username)


@app.route('/perform_deletion', methods=['POST'])
def perform_deletion():
    selected_locations = request.form.getlist('locationsToDelete[]')
    print(selected_locations)
    username = request.form['username']
    match = [re.search(r'\d+', string).group() for string in selected_locations]
    print(match)
    for i in match:
        i=int(i)
        print(i)
        query=query_db(sq.query16,[i])
        print("Q",query)
        query_2=query_db(sq.query17,query)
        print(query_2)
        if (len(query_2)!=0):
            print("Q2",query_2[0][0])
            for i in range(0,len(query_2)):
                print("i",query_2[i][0])
                delete_from_db(sq.query18,[query_2[i][0]])
                delete_from_db(sq.query19,[query_2[i][0]])
        delete_from_db(sq.query20,query)
        delete_from_db(sq.query21,[i])
    return render_template('options.html', username=username)

@app.route('/add_device/<username>', methods=['GET', 'POST'])
def add_device(username):
    query_1=query_db(sq.query3,[username])
    query_2=query_db(sq.query22,[query_1[0][0]])
    device=query_db(sq.query23,[])
    #print(device)
    formatted_output = [f"{item[0]} : {item[1]}" for item in device]
    formatted_output_list = [formatted_output]
    devices=[]
    for i in range(0,len(formatted_output_list[0])):
        devices.append(formatted_output_list[0][i])
    user_locations=[]
    for i in query_2:
        query_3=query_db(sq.query24,[i[0]])
        cleaned_str = re.sub(r'[^\w\s,]', '', query_3[0][0])
        cleaned_str = cleaned_str.replace(',', ' ')
        cleaned_str = ' '.join(cleaned_str.split())
        user_locations.append(cleaned_str)
    return render_template('add_device.html', username=username,serviceLocations=user_locations,devices=devices)

@app.route('/submit-device-model/<username>', methods=['POST'])
def submit_device(username):
    service_location = request.form.get('serviceLocation')
    device  = request.form['device']
    type, modelnumber = device.split(" : ")
    match = re.search(r'\d+', service_location)
    if match:
        number = match.group()
    else:
        print("No match found")
    user_5=query_db(sq.query25, [], one=True)
    if user_5[0] is not None:  # Check if the result is not None
        id = int(user_5[0])  # Convert the first element of the tuple to int
    else:
        id = 1  # Start from 1 if there are no entries
    id += 1  # Increment the id
    insert_db(sq.query26,[id,number,type,modelnumber])
    return render_template('options.html', username=username)


@app.route('/delete_device/<username>',methods=['GET', 'POST'])
def render_custom_dropdown(username):
    query_1=query_db(sq.query3,[username])
    query_3=query_db(sq.query27,[query_1[0][0]])#many
    #user_devices=[]
    user_locations=[]
    for i in query_3:
        query_3=query_db(sq.query28,[i[0]])
        query_5=query_db(sq.query29,[query_3[0]])
        query_4=query_db(sq.query30,[i[0]])
        for i in range(0,len(query_4)):
            if (len(query_3) != 0 and len(query_4) != 0):
                # Removing all punctuation using regular expression
                string_data = re.sub(r',', ' ', query_5[0][0])
                cleaned_data = re.sub(r'[^\w\s]', '', string_data)
                string_data_2 = re.sub(r',', ' ', query_4[i][0])
                # Removing all other punctuation (except spaces)
                cleaned_data_2 = re.sub(r'[^\w\s]', '', string_data_2)
                device_location=str(cleaned_data_2)+"  at  "+str(cleaned_data)
                print(i,device_location)
                user_locations.append(device_location)
            else:
                continue
    print(user_locations)
    userSuppliedList = user_locations 
    return render_template('delete_device.html', username=username, userSuppliedList=userSuppliedList)

@app.route('/device_delete/<username>', methods=['POST'])
def handle_selection(username):
    selected_options = request.form.getlist('selectedOptions[]')
    extracted_numbers = []

    # Extracting numbers
    for item in selected_options:
        matches = re.findall(r'^\d+', item)
        extracted_numbers.extend(matches)
    # Convert extracted strings to integers
    extracted_numbers = [int(num) for num in extracted_numbers]
    #print(extracted_numbers)  # Output will be [5, 6]
    # Handle the selected option (e.g., delete operation)
    for i in extracted_numbers:
        print(i)
        delete_from_db(sq.query31,[i])
        delete_from_db(sq.query32,[i])
    # Redirect or return a response as needed
    return render_template('options.html', username=username)




@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    #username = query_db("SELECT username FROM customers WHERE customerid = %s",[id],one = True)
    #print(username[0])
    return render_template('dashboard.html', username=username)

#Archit Code
@app.route('/energy-consumptions/<username>', methods=['GET', 'POST'])
def energy_consumption_views(username):
    # You can pass necessary data to the template if needed
    return render_template('energy_consumption_views.html', username=username)

@app.route('/get-energy-data/<username>',methods=['GET', 'POST'])
def get_energy_data(username):
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    print(start_date)
    data = fetch_data_between_dates(start_date, end_date,username)
    return jsonify(data)

def fetch_data_between_dates(start, end,username):
    # Assuming query_db is a function that executes a SQL query and returns the result
    print("get energy data username", username)
    query = sq.query33
    data = query_db(query, [start, end,username])
    print(data)
    # Format the data as needed for the chart
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return {'labels': labels, 'values': values}

@app.route('/get-device-consumption-data/<username>',methods=['GET', 'POST'])
def get_device_consumption_data(username):
    month = request.args.get('month')
    year = request.args.get('year')
    # Fetch data from your database based on the selected month
    #print(month,year,username)
    data = fetch_device_consumption_for_month(month,year,username)
    #print("data for view 2",data)
    print(month,year)
    return jsonify(data)

@app.route('/display-pie-chart/<username>')
def display_pie_chart(username):
    query = sq.query34
    userid=query_db(sq.query3,[username])
    data = query_db(query,userid)
    user_energy = data[0][0] # Fetch user's energy
    total_energy = data[0][1] # Fetch total energy
    print(user_energy)

    # Return as a JSON response
    return jsonify([user_energy, total_energy])



@app.route('/get_device_address_data/<username>',methods=['GET', 'POST'])
def get_device_address_data(username):
    query=query_db('''SELECT 
    D.DeviceID, 
    DM.Type AS DeviceType,
    DM.Manufacturer AS DeviceName,
    A.AddressLine1, A.AddressLine2, A.City, A.State, A.Country, A.ZipCode,
    DE.Timestamp
    FROM 
        Customers C
    JOIN 
        ServiceLocations SL ON C.CustomerID = SL.CustomerID
    JOIN 
        Address A ON SL.AddressID = A.AddressID
    JOIN 
        Devices D ON SL.LocationID = D.LocationID
    JOIN 
        DeviceModels DM ON D.ModelNumber = DM.ModelNumber
    JOIN 
        DeviceEvents DE ON D.DeviceID = DE.DeviceID
    WHERE 
        C.Username = %s''',[username])
    #print(query)
    formatted_data = [
    f"{item[0]} :{item[1]}: {item[2]} at {', '.join([str(elem) for elem in item[3:9] if elem])} at time {item[9]}" for item in query]
    #print(formatted_data)

    user_provided_list=formatted_data
    return jsonify(user_provided_list)
    #return render_template('energy_consumption_views.html', username=username, userSuppliedList=userSuppliedList)

@app.route('/get_savings_data/<username>',methods=['GET', 'POST'])
def get_related_options(username):
    selected_location = request.args.get('selectedLocation')
    parts = selected_location.split(':')
    device_id = parts[0].strip()
    timestamp = re.search(r'\d{4}-\d{2}-\d{2}', selected_location).group()
    result = [device_id, timestamp]
    print("view3",result)
    query=query_db(sq.query38,result)
    print("Result of the query",query)
    labels = [[row[1],row[3]] for row in query]
    print("L",labels)
    formatted_datetimes = [[dt1.strftime('%Y-%m-%d %H:%M:%S'), dt2.strftime('%Y-%m-%d %H:%M:%S')] for dt1, dt2 in labels]
    print(formatted_datetimes)
    values = [[float(row[2]),float(row[4]) ]for row in query]
    print(values)
    print("Labels are ",labels)
    print("Values are ",values)
    return {'labels': formatted_datetimes, 'values': values}


def fetch_device_consumption_for_month(month,year,username):
    print(username,month,year)
    query =sq.query35
    data = query_db(query,(username,month,year))
    print(data)
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return {'labels': labels, 'values': values}

@app.route('/get_service_locations/<username>',methods=['GET', 'POST'])
def get_service_locations(username):
    print(username)
    query = sq.query36
    data = query_db(query,[username])
    print(data)
    return jsonify(data)

@app.route('/get_device_data/<username>',methods=['GET', 'POST'])
def get_device_data(username):
    selected_location = request.args.get('selectedLocation')
    print(selected_location)
    query = sq.query37
    
    device_data = query_db(query, [selected_location])
    print("Device data is",device_data)
    formatted_data = [{'device_type': row[1], 'count': row[0]} for row in device_data]

    return jsonify(formatted_data)

if __name__ == '__main__':
    app.run(debug=True)
