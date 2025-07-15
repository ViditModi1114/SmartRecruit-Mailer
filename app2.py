from flask import Flask, request, jsonify, render_template
from groq import Groq
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the Groq client with your API key from environment variable
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logging.error("API_KEY not found in environment variables")
    raise ValueError("API_KEY is required")
client = Groq(api_key=API_KEY)

def extract_skills_from_job_description(job_description):
    """Extract skills from the job description."""
    if not job_description:
        return []
    return [skill.strip() for skill in job_description.split(",") if skill.strip()]

def generate_email_groq(company_name, job_description, skills, your_name, your_position, your_contact):
    """
    Generate a professional email using the updated prompt with Groq API.
    """
    skills_str = ", ".join(skills) if skills else "a diverse skill set to meet all your job requirements"

    # Updated email template
    prompt = f"""
    Write a professional and persuasive email to offer our company's services in providing skilled employees for a specific job opening. The email should be clear, polished, and free of any grammatical errors. Structure it into six distinct paragraphs covering the following points:

    1. Begin with a warm and professional introduction.
    2. State our interest in the job opening and emphasize our ability to meet the role's specific requirements.
    3. Showcase our company's expertise in sourcing and supplying highly skilled professionals tailored to the job description.
    4. Clearly explain how our employees' expertise aligns with the required skills and competencies, reinforcing confidence in our ability to deliver exceptional results.
    5. Highlight the benefits of partnering with our company, including our proven track record, commitment to excellence, and dedication to client satisfaction.
    6. End with a strong call to action, encouraging further discussion or a meeting to explore this opportunity.

    Use the following placeholders in the email:
    - {company_name}: The name of our company.
    - {skills_str}: The list of essential skills required for the job.
    - {your_name}: Your name.
    - {your_position}: Your position in the company.
    - {your_contact}: Your contact information.

    Subject: Providing Skilled Employees for Your Job Opening

    Dear Hiring Manager,

    I hope this message finds you well. My name is {your_name}, and I am {your_position} at {company_name}. I am reaching out regarding the job opening you posted, as we believe that our company is uniquely positioned to help meet your staffing needs.

    At {company_name}, we specialize in connecting organizations like yours with skilled professionals who possess the specific expertise required for roles such as the one described in your job posting. Based on the provided job description, we understand that the following skills are critical: {skills_str}.

    Our team comprises highly qualified individuals who not only possess these skills but also have a proven track record of success in their respective fields. With our extensive experience in matching talent with opportunities, we are confident that we can provide employees who will contribute meaningfully to your organization’s goals.

    Over the years, {company_name} has earned a reputation for delivering reliable, high-quality staffing solutions that align perfectly with our clients’ needs. We take pride in our commitment to excellence and client satisfaction, and we are confident that our expertise can add significant value to your team.

    I would greatly appreciate the opportunity to discuss how {company_name} can support your staffing requirements. Please feel free to contact me directly at {your_contact} or let me know a convenient time for us to connect.

    Thank you for considering {company_name} as your partner in this endeavor. I look forward to the possibility of working together and contributing to your organization's success.

    Best regards,  
    {your_name}  
    {your_position}  
    {company_name}  
    {your_contact}
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        email_content = completion.choices[0].message.content.strip()
        logging.info("Email content generated successfully.")
        return email_content
    except Exception as e:
        logging.error(f"Error generating email with Groq: {e}")
        return "An error occurred while generating the email. Please try again later."

@app.route('/', methods=['GET'])
def index():
    """
    Render the main HTML template.
    """
    return render_template('index2.html')

@app.route('/process', methods=['POST'])
def process():
    """
    Handle form submission, validate input, and generate the email content.
    """
    try:
        # Log the received data
        logging.debug(f"Received form data: {request.form}")

        # Retrieve and validate form data
        required_fields = ['company_name', 'job_description', 'your_name', 'your_position', 'your_contact']
        form_data = {field: request.form.get(field) for field in required_fields}
        missing_fields = [field for field, value in form_data.items() if not value]

        if missing_fields:
            error_message = f"Missing fields: {', '.join(missing_fields)}"
            logging.warning(error_message)
            return jsonify({'error': error_message}), 400

        # Extract skills from the job description
        extracted_skills = extract_skills_from_job_description(form_data['job_description'])

        # Generate the email
        email_content = generate_email_groq(
            company_name=form_data['company_name'],
            job_description=form_data['job_description'],
            skills=extracted_skills,
            your_name=form_data['your_name'],
            your_position=form_data['your_position'],
            your_contact=form_data['your_contact']
        )

        # Return the generated email as JSON
        return jsonify({'email_content': email_content})
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)