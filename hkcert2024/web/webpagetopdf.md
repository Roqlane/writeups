This chall was a guided one.

The website is a pdf renderer: you enter an url, it returns the pdf version of html page.

![image](https://github.com/user-attachments/assets/fa97f22c-f970-4055-9a4e-ddfe970685bb)

To perform this operation, the app uses the `wkhtmltopdf` tool:

```python
app.route('/process', methods=['POST'])
def process_url():
    # Get the session ID of the user
    session_id = request.cookies.get('session_id')
    html_file = f"{session_id}.html"
    pdf_file = f"{session_id}.pdf"

    # Get the URL from the form
    url = request.form['url']
    
    # Download the webpage
    response = requests.get(url)
    response.raise_for_status()

    with open(html_file, 'w') as file:
        file.write(response.text)

    # Make PDF
    stdout, stderr, returncode = execute_command(f'wkhtmltopdf {html_file} {pdf_file}')

    if returncode != 0:
        return f"""
        <h1>Error</h1>
        <pre>{stdout}</pre>
        <pre>{stderr}</pre>
        """
        
    return redirect(pdf_file)
```

When looking for wkhtmltopdf vulnerabilities, we encounter this article https://www.virtuesecurity.com/kb/wkhtmltopdf-file-inclusion-vulnerability-2/ which explains very well how to exploit the tool. In our case, what we need to do in order to get the flag is to set up a remote server containing some html that requests the local flag file. However, this will not be enough to trigger the LFI as the application prevents access to local file. To bypass this, we need a way to add `--enable-local-file-access` to the command.

When looking to the source code, we see that it uses the id of the user to create the name of the pdf file. This is our way to go.

![image](https://github.com/user-attachments/assets/5954277f-7ec0-48fb-9375-18bef8138ac8)

For the server part, we uses https://jsbin.com

![image](https://github.com/user-attachments/assets/d8b7ff45-43b9-41ab-9fd5-1bd91b1dd882)

Send the custom to url to the app with the modified cookie, remove the `--enable-local-file-access%20` of the filename and here's the flag.
