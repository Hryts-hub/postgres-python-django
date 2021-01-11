from celery import shared_task
from time import sleep, time
from manager.models import TableAggregate, GitInfo
from pip._vendor.requests import post, get
from datetime import datetime


@shared_task
def hello(pause):
	sleep(pause)
	return "hello, task done"


@shared_task
def create_aggregate(user_id):
	sleep(10)
	TableAggregate.objects.create(user_id=user_id, result=int(time()))


# @shared_task
# def just_taks():
# 	return "hello done"

@shared_task
def git_info():
	users = GitInfo.objects.all()
	for user in users:
		login = user.git_login
		user_id = user.user_id
		url2 = f"https://api.github.com/users/{login}/repos"
		response = get(url2)
		repos = [i['name'] for i in response.json()]
		GitInfo.objects.all().filter(user_id=user_id).update(
			user_id=user_id,
			date=str(datetime.now()),
			result=str(repos),
			git_login=login
		)
