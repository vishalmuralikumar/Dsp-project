import smtplib
from email.message import EmailMessage

import joblib
import pandas as pd
from dotenv import dotenv_values

from config import MODEL, LABEL
from machineTraining import pre_processing_data


def send_mail(message: str) -> str:
    """Send email via my private email to """
    try:
        config = dotenv_values('.env')
        sender = config.get('SENDER')
        password = config.get('PASSWORD')
        recipient = config.get('RECIPIENT')
        email = EmailMessage()
        email["From"] = sender
        email["To"] = recipient
        email["Subject"] = "Test Email"
        email.set_content(message)

        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()
        smtp.login(user=sender, password=password)
        smtp.sendmail(from_addr=sender, to_addrs=recipient, msg=email.as_string())
        smtp.quit()
        return 'Send Successfully'
    except Exception as e:
        print(e)
        return 'Failed Successfully'


def make_predictions(input_data: pd.DataFrame) -> pd.DataFrame:
    inference_model = joblib.load(MODEL)
    inference_data = pre_processing_data(input_data, is_training=False)
    input_data[LABEL] = inference_model.predict(inference_data)
    input_data[LABEL] = input_data[LABEL].abs()
    return input_data


if __name__ == '__main__':
    user_data_df = pd.read_csv('../model/auto.csv')
    predictions = make_predictions(user_data_df.head(5))
    print(predictions)
    #
    # send_status = send_mail('hi')
    # print(send_status)
