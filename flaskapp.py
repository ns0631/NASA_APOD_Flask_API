#When using this program, please be patient with the loading process.
from flask import Flask, render_template, request
from PIL import Image
import requests, json, os, datetime

#Makes main instance
app = Flask(__name__)

#Makes homepage.html the root page
@app.route('/')
def student():
   return render_template('homepage.html')

@app.route('/result', methods = ['POST', 'GET'])
def result():
    #If a post request is made
    if request.method == 'POST':
        #Gets the result of the request, which is the date
        result = request.form
        user_date = result['Date']

        #Tests whether the date given is legitimate
        try:
            real_date = datetime.datetime.strptime(user_date, '%Y-%m-%d')
        except ValueError:
            return render_template('format.html')
        else:
            start_date = datetime.datetime.strptime('1995-06-20', '%Y-%m-%d')
            end_date = datetime.datetime.today()

            #the date cannot be in the future
            if real_date > end_date:
                return render_template('future.html')
            #1995-06-20 was the date of the first picture
            elif real_date < start_date:
                return render_template('past.html')
            else:
                #Request is made with my API key
                request_base = 'https://api.nasa.gov/planetary/apod?api_key=v4IsLQx1M8ssN5Rtc1KBBNczkz2p4vHtK81gXeap&date=%s'
                request_info = request_base % user_date
                try:
                    main_request = requests.get(request_info)
                    #Info is parsed with json
                    request_content = main_request.content
                    main_request.close()
                    json_content = json.loads(request_content)
                except requests.exceptions.ConnectionError:
                    #Prepares for network errors
                    return render_template('connectionfailure.html')
                else:
                    #If no HD version of the Image exists, the non-HD version will be used.
                    try:
                        img_url = json_content['hdurl']
                    except KeyError:
                        img_url = json_content['url']

                    #When the request is made without any dates, the API's default is today.
                    if len(user_date) < 2:
                        user_date = 'Today'

                    try:
                        #The image is loaded.
                        img_page = requests.get(img_url)
                        img_content = img_page.content
                        img_page.close()
                    except requests.exceptions.ConnectionError:
                        #Prepares for network errors
                        return render_template('connectionfailure.html')
                    else:
                        #PNG/JPEG file is written
                        img_file = open('newimg.png', 'wb')
                        img_file.write(img_content)
                        img_file.close()

                        #Image file is converted to PDF
                        filename = 'NASA\'s Photo on %s.pdf' % user_date
                        png_image = Image.open('newimg.png')
                        pdf_image = png_image.convert('RGB')
                        pdf_image.save(filename)
                        #The original picture is removed
                        os.remove('newimg.png')

                        #The user sees a new page containing the caption
                        return render_template('result.html', result={'Caption': json_content['explanation']})


if __name__ == '__main__':
    #Runs app
    app.run(debug=True)
