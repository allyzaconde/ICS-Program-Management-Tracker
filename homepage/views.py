from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import csv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from operator import itemgetter
from collections import Counter

import perfplot

# superuser superuserpassword1234
# testuser march1400

#gets the data from google excel sheets
def get_data(filename, worksheetno):
    #get data from GSheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('templates/key.json',scope)
    gc = gspread.authorize(creds)

    sheet = gc.open(filename) #mockdata

    result = sheet.get_worksheet(worksheetno).get_all_records()
    return result

#algorithm 1
def get_count(labels, mem_type, result, get):
    data_count = []
    count = 0

    # get data from results using list comprehension
    member = list(k.get(get) for k in result if k.get('Program') == mem_type)
    total = dict(Counter(sub[get] for sub in result))

    # graph data logic
    for period in labels:
        sem = period.split(" ")[0]
        year = period.split(" ")[2]
        year1 = year.split("-")[0]
        year2 = year.split("-")[1]

        if sem == "1st":
            half_1 = year1 + "-08-01"
            half_2 = year2 + "-01-31"
        else:
            half_1 = year2 + "-02-01"
            half_2 = year2 + "-07-31"

        if mem_type == "Total":
            for x, y in total.items():
                if x >= half_1 and x <= half_2:
                    count = count + y
            data_count.append(count)
            count = 0
        else:
            data = list(1 for x in member if x >= half_1 and x <= half_2)
            data_count.append(len(data))
        
    return data_count

#algorithm 2
def for_loop(labels, mem_type, result):
    data_count = []
    count = 0
    
    # get data from results using for loop
    member = []
    for k in result:
        if k.get('Program') == mem_type:
            member.append(k.get('Date of Admission'))
    
    total = dict(Counter(sub['Date of Admission'] for sub in result))

    # graph data logic
    for period in labels:
        sem = period.split(" ")[0]
        year = period.split(" ")[2]
        year1 = year.split("-")[0]
        year2 = year.split("-")[1]

        if sem == "1st":
            half_1 = year1 + "-08-01"
            half_2 = year2 + "-01-31"
        else:
            half_1 = year2 + "-02-01"
            half_2 = year2 + "-07-31"

        if mem_type == "Total":
            for x, y in total.items():
                if x >= half_1 and x <= half_2:
                    count = count + y
            data_count.append(count)
            count = 0
        else:
            for x in member:
                if x >= half_1 and x <= half_2:
                    count = count + 1
            data_count.append(count)
            count = 0
        
    return data_count

result = get_data("mockdata", 0)
result2 = get_data("mockdata", 2)
result3 = get_data("mockdata", 3)
labels_sem =  ['1st Sem 2015-2016', '2nd Sem 2015-2016', '1st Sem 2016-2017', '2nd Sem 2016-2017', '1st Sem 2017-2018', '2nd Sem 2017-2018', '1st Sem 2018-2019', '2nd Sem 2018-2019', '1st Sem 2019-2020', '2nd Sem 2019-2020', '1st Sem 2020-2021', '2nd Sem 2020-2021', '1st Sem 2021-2022', '2nd Sem 2021-2022']

#benchmarking
def benchmarking():
    labels_sem =  ['1st Sem 2015-2016', '2nd Sem 2015-2016', '1st Sem 2016-2017', '2nd Sem 2016-2017', '1st Sem 2017-2018', '2nd Sem 2017-2018', '1st Sem 2018-2019', '2nd Sem 2018-2019', '1st Sem 2019-2020', '2nd Sem 2019-2020', '1st Sem 2020-2021', '2nd Sem 2020-2021', '1st sem 2021-2022', '2nd sem 2021-2022']
    member_type = "BSCS" 
    out = ''
    out = perfplot.bench(
        setup = lambda n: [{'Student No.': 201596939, 'Name': 'Will Dafo', 'Adviser': 'Candidus Dennis', 'Program': 'MIT', 'Gender': 'Male', 'Date of Birth': '1996-05-14', 'Marital Status': 'Single', 'Contact No.': 9509661316, 'Email Address': 'mnemonic@icloud.com', 'Home Address': 'U. Corpus St. Masbate', 'Date of Admission': '2016-02-17', 'Status': 'Active'} for i in range(n)],
        kernels = [
            lambda a: get_count(labels_sem, member_type, a),
            lambda a: for_loop(labels_sem, member_type, a)
        ],
        n_range = [2**k for k in range(8,24)],
        labels = ["List Comprehension", "Nested Loop"],
        xlabel = "Input Size"
    )
    print(out)
    out.show()
    out.save("perf.png", transparent=True, bbox_inches="tight")

def change_labels(labels,index):
    newlabels = labels

    sem = newlabels[index].split(" ")[0]
    year = newlabels[index].split(" ")[2]
    year1 = year.split("-")[0]
    year2 = year.split("-")[1]

    newsem = ''
    if sem == "1st":
        newsem = "2nd"
    else:
        newsem = "1st"

    if index == 0:
        #add previous sem
        if sem == "1st":
            newsem = "2nd"
            newlabels.insert(0, newsem + " Sem " + str(int(year1) - 1) + "-" + year1)
            
        else:
            newsem = "1st"
            newlabels.insert(0, newsem + " Sem " + year1 + "-" + year2)
        newlabels.pop(len(newlabels)-1)
    else:
        #add new sem
        if sem == "1st":
            newsem = "2nd"
            newlabels.append(newsem + " Sem " + year1 + "-" + year2)
        else:
            newsem = "1st"
            newlabels.append(newsem + " Sem " + year2 + "-" + str(int(year2) + 1))
        newlabels.pop(0)
    
    return newlabels


@login_required(login_url="/login")
def students(request):

    #add or delete sem
    newsem = request.GET.get('sem', 'default')
    if newsem == "add":
        change_labels(labels_sem,len(labels_sem)-1)
    elif newsem == "delete":
        change_labels(labels_sem,0)

    # member type graph
    member_type = request.GET.get('member_type', 'BSCS')
    data_count = get_count(labels_sem, member_type, result, 'Date of Admission')
    
        # graph design
    if member_type == "BSCS":
        bgcolor = "rgb(21, 138, 73, 0.5)"
        title = "BS Computer Science"
    elif member_type == "MIT":
        bgcolor = "rgb(110, 189, 13, 0.5)"
        title = "Master of Information Technology"
    elif member_type == "MSCS":
        bgcolor = "rgb(195, 103, 51, 0.5)"
        title = "Master of Science in Computer Science" 
    elif member_type == "PhD":
        bgcolor = "rgb(233, 164, 43, 0.5)"
        title = "PhD (Computer Science)"
    elif member_type == "Total":
        bgcolor = "rgb(255, 212, 20, 0.5)"
        title = "Total"

    # order and direction of table values
    order_by = request.GET.get('order_by', 'Student No.')
    direction = request.GET.get('direction', 'asc')

    if direction == "asc":
        table = sorted(result, key=itemgetter(order_by))
    elif direction == "desc":
        table = sorted(result, key=itemgetter(order_by), reverse=True)

    # pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(table, 6)
    try:
        table_data = paginator.page(page)
    except PageNotAnInteger:
        table_data = paginator.page(1)
    except EmptyPage:
        table_data = paginator.page(paginator.num_pages)
    currpage = paginator.page(page)

    # total count header
    count_total = dict(Counter(sub['Program'] for sub in result))

    if 'BSCS' in count_total:
        bscs_all = count_total['BSCS']
    else:
        bscs_all = 0

    if 'MIT' in count_total:
        mit_all = count_total['MIT']
    else:
        mit_all = 0    

    if 'MSCS' in count_total:
        mscs_all = count_total['MSCS']
    else:
        mscs_all = 0

    if 'PhD' in count_total:
        phd_all = count_total['PhD']
    else:
        phd_all = 0

    # webpage differentiation
    table_header = ['Student No.', 'Name', 'Adviser', 'Program', 'Gender', 'Date of Birth', 'Marital Status', 'Contact No.', 'Email Address', 'Home Address', 'Date of Admission', 'Status']        
    member = 'student'
    
    return render(request, 'members.html', {
        'bscs': bscs_all,
        'mit': mit_all,
        'mscs': mscs_all,
        'phd': phd_all,
        'table': table_data,
        'order_by': order_by,
        'direction': direction,
        'currpage': currpage,
        'bgcolor': bgcolor,
        'title': title,
        'data_count': data_count,
        'labels_sem': labels_sem,
        'table_header': table_header,
        'member': member,
        'member_type': member_type
    })

@login_required(login_url="/login")
def faculty(request):

    #add or delete sem
    newsem = request.GET.get('sem', 'default')
    if newsem == "add":
        change_labels(labels_sem,len(labels_sem)-1)
    elif newsem == "delete":
        change_labels(labels_sem,0)

    # member type graph
    member_type = request.GET.get('member_type', 'BSCS')
    data_count = get_count(labels_sem, member_type,result2,'Start of Appointment')

        # graph design
    if member_type == "BSCS":
        bgcolor = "rgb(21, 138, 73, 0.5)"
        title = "BS Computer Science"
    elif member_type == "MIT":
        bgcolor = "rgb(110, 189, 13, 0.5)"
        title = "Master of Information Technology"
    elif member_type == "MSCS":
        bgcolor = "rgb(195, 103, 51, 0.5)"
        title = "Master of Science in Computer Science" 
    elif member_type == "PhD":
        bgcolor = "rgb(233, 164, 43, 0.5)"
        title = "PhD (Computer Science)"
    elif member_type == "Total":
        bgcolor = "rgb(255, 212, 20, 0.5)"
        title = "Total"

    # order and direction of table values
    order_by = request.GET.get('order_by', 'Faculty No.')
    direction = request.GET.get('direction', 'asc')

    if direction == "asc":
        table = sorted(result2, key=itemgetter(order_by))
    elif direction == "desc":
        table = sorted(result2, key=itemgetter(order_by), reverse=True)

    # pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(table, 6)
    try:
        table_data = paginator.page(page)
    except PageNotAnInteger:
        table_data = paginator.page(1)
    except EmptyPage:
        table_data = paginator.page(paginator.num_pages)
    currpage = paginator.page(page)

    # total count header
    count_total = dict(Counter(sub['Program'] for sub in result2))

    print(count_total.keys())

    if 'BSCS' in count_total:
        bscs_all = count_total['BSCS']
    else:
        bscs_all = 0

    if 'MIT' in count_total:
        mit_all = count_total['MIT']
    else:
        mit_all = 0    

    if 'MSCS' in count_total:
        mscs_all = count_total['MSCS']
    else:
        mscs_all = 0

    if 'PhD' in count_total:
        phd_all = count_total['PhD']
    else:
        phd_all = 0

    # webpage differentiation
    table_header = ['Faculty No.', 'Name', 'Program', 'Position', 'Gender', 'Start of Appointment', 'End of Appointment', 'Status']        
    member = 'faculty'

    return render(request, 'members.html', {
        'bscs': bscs_all,
        'mit': mit_all,
        'mscs': mscs_all,
        'phd': phd_all,
        'table': table_data,
        'order_by': order_by,
        'direction': direction,
        'currpage': currpage,
        'bgcolor': bgcolor,
        'title': title,
        'data_count': data_count,
        'labels_sem': labels_sem,
        'table_header': table_header,
        'member': member,
        'member_type': member_type
    })


@login_required(login_url="/login")
def program(request):
    table = ''

    # order and direction of table values
    order_by = request.GET.get('order_by', 'Class No.')
    direction = request.GET.get('direction', 'asc')

    if direction == "asc":
        table = sorted(result3, key=itemgetter(order_by))
    elif direction == "desc":
        table = sorted(result3, key=itemgetter(order_by), reverse=True)

    # pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(table, 6)
    try:
        table_data = paginator.page(page)
    except PageNotAnInteger:
        table_data = paginator.page(1)
    except EmptyPage:
        table_data = paginator.page(paginator.num_pages)
    currpage = paginator.page(page)

    table_header = ['Class No.', 'Course No.', 'Title', 'Section', 'Class Component', 'Units', 'Career', 'Grading Basis', 'Enrollment Requirements', 'Status']

    return render(request, 'program.html', {
        'table': table_data,
        'table_header': table_header,
        'currpage': currpage,
        'order_by': order_by,
        'direction': direction
    })


@login_required(login_url="/login")
def about(request):
    return render(request, 'about.html')

@login_required(login_url="/login")
def search(request):
    query = request.GET.get('q')
    query = query.lower()

    student_result = []
    faculty_result = []
    course_result = []

    for sub in result:
        for s in sub.values():
            value = str(s).lower()
            if query in value:
                student_result.append(sub)
                continue

    for sub in result2:
        for s in sub.values():
            value = str(s).lower()
            if query in value:
                faculty_result.append(sub)
                continue

    for sub in result3:
        for s in sub.values():
            value = str(s).lower()
            if query in value:
                course_result.append(sub)
                continue
    
    student_header = ['Student No.', 'Name', 'Adviser', 'Program', 'Gender', 'Date of Birth', 'Marital Status', 'Contact No.', 'Email Address', 'Home Address', 'Date of Admission', 'Status']        
    faculty_header = ['Faculty No.', 'Name', 'Program', 'Position', 'Gender', 'Start of Appointment', 'End of Appointment', 'Status']        
    course_header = ['Class No.', 'Course No.', 'Title', 'Section', 'Class Component', 'Units', 'Career', 'Grading Basis', 'Enrollment Requirements', 'Status']


    return render(request, 'search.html', {
        'student_result': student_result,
        'faculty_result': faculty_result,
        'course_result': course_result,
        'student_header': student_header,
        'faculty_header': faculty_header,
        'course_header': course_header
    })


#downloading table
def export(request):
    response = HttpResponse(content_type='text/csv')

    print(request.build_absolute_uri())

    writer = csv.writer(response)

    writer.writerow(['Student No', 'Name', 'Adviser', 'Program', 'Gender', 'Date of Birth', 'Marital Status', 'Contact No', 'Email Address', 'Home Address', 'Date of Admission', 'Status'])
    result = get_data("mockdata", 0)
    for data in result:
        writer.writerow(list(data.values()))

    writer.writerow(['Faculty No.', 'Name', 'Program', 'Position', 'Gender', 'Start of Appointment', 'End of Appointment', 'Status'])
    result = get_data("mockdata", 2)
    for data in result:
        writer.writerow(list(data.values()))

    writer.writerow(['Class No.', 'Course No.', 'Title', 'Section', 'Class Component', 'Units', 'Career', 'Grading Basis', 'Enrollment Requirements', 'Status'])
    result = get_data("mockdata", 3)
    for data in result:
        writer.writerow(list(data.values()))

    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    return response

#sign up
def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/students')
    else:
        form = RegistrationForm()

    return render(request, 'registration/sign_up.html', {
        'form': form
    })