from instagrapi import Client
from pydantic_settings import BaseSettings 
import csv
import re
import argparse

class Settings(BaseSettings):
    username: str
    password: str
    proxy: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

INST_USERNAME = settings.username
INST_PASSWORD = settings.password
POST_COUNT = 10
SLEEP_TIME = 5

cl = Client()
cl.login(username=INST_USERNAME, password=INST_PASSWORD)


def extract_username_from_url(url):
    try:
        pattern = r'instagram\.com/([A-Za-z0-9._]+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Некорректная ссылка на Instagram")
    except Exception as e:
        print(e)

def parse_url():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='inst link')
    return parser.parse_args()
## url example https://www.instagram.com/jasonstatham/


def get_account_info(url:str) -> dict:
    try:
        username = extract_username_from_url(url)

        user_id = cl.user_id_from_username(username)
        user_info = cl.user_info(user_id)

        medias = cl.user_medias(user_id, amount=POST_COUNT, sleep=SLEEP_TIME)
        data = []

        for media in medias:
            post_info = {
                "caption" : media.caption_text if media.caption_text else 'Нет описания',
                "likes" : media.like_count,
                "comments": media.comment_count,
                "date": media.taken_at.strftime("%Y-%m-%d")            
            }
            data.append(post_info)

        if data:
            with open('csv_data.csv', 'w', newline="", encoding="utf-8") as csvfile:
                fieldnames = ["caption", "likes", "comments", "date"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                print("Данные о постах сохранены")
        else:
            print("Неудача")


        return {
            "followers" : user_info.follower_count,
            "posts" : user_info.media_count
        }
    
    except Exception as e:
        print(f'Ошибка: {e}')
    


if __name__ == "__main__":
    arg = parse_url()
    data = get_account_info(arg.url)
    print(data)

