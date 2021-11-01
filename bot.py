#  https://www.codifylab.com/kak_sozdat_telegram_bota
import  requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import configparser
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN

#bot = Bot(token=config.Token)
#dp = Dispatcher(bot)
token = TOKEN
print("Бот запущен. Нажмите Ctrl+C для завершения")

def on_start(update, context):
	chat = update.effective_chat
	context.bot.send_message(chat_id=chat.id, text='Привет, бот ведет поиск статей по ключевым словам на сайте : ' + 'habr.com' + '\n' +
                                                   'Поиск ведется до нахождения любого слова из списка в preview-тексте или полном тексте статьи' + '\n\n' +
												   'Введите список ключевых слов для поиска ( через запятую )')

def on_message(update, context):
	chat = update.effective_chat
	text = update.message.text
	try:
		KEYWORDS = str(text).split(',')
		chat = update.effective_chat
		context.bot.send_message(chat_id=chat.id, text=KEYWORDS)
		#print (KEYWORDS)
		url_start = 'https://habr.com/ru/all/'  # starting url
		num_article = 0
		for npage in range(1, 2):
			url = url_start + 'page' + str(npage)
			print('Downloading page %s...' % url)
			res = requests.get(url)
			res.raise_for_status()
			soup = BeautifulSoup(res.text, 'lxml')
			# print(soup)
			ArticleElem = []
			ArticleElem = soup.find_all('article', class_='tm-articles-list__item')
			print ('ArticleElem' + str(len(ArticleElem)))
			#    print(BooksElem)
			if len(ArticleElem) > 0:
				print('Страница ' + str(npage))
				for area in ArticleElem:
					# print(area)
					article_preview = area.find('div', class_='article-formatted-body').text
					area_datatime = area.find('span', class_='tm-article-snippet__datetime-published')
					#print(area_datatime)
					if area_datatime:
						try:
							article_datatime = area_datatime.find('time')['title']
							#print (area_datatime)
							#print(article_datatime)
							pos2 = article_datatime.find(',')
							article_data = article_datatime[0:pos2]
						except:
							print('ошибка извлечения даты')
							print(area)
							article_data = '????-??-??'
						# print(article_datatime)

						# print(article_data)
					else:
						continue
					area_title = area.find('a', class_='tm-article-snippet__title-link')
					# print(area_title)
					try:
						article_title = area_title.find('span').text
						article_href = 'https://habr.com' + area.find('a', class_='tm-article-snippet__title-link')[
							'href']
					except:
						article_title = ''
						article_href = ''
					# print(article_title + ' ' + article_href)
					try:
						res = requests.get(article_href)
						soup = BeautifulSoup(res.text, 'lxml')
						ArticleText = []
						ArticleText = soup.find('div', class_='article-formatted-body')
						article_text = ArticleText.text
					# res.raise_for_status()
					except:
						print('ошибочный адрес статьи  ' + article_href)
						continue
					full_text = article_preview + article_text
					for key_word in KEYWORDS:
						if key_word.lower() in full_text.lower():
							# print(article_href)
							num_article = num_article + 1
							bot_output = str(num_article) + "   " + article_data + ' - ' + article_title + ' - ' + article_href[8:]
							print(bot_output)
							context.bot.send_message(chat_id=chat.id, text=bot_output)
							break
						else:
							continue

		#number = float(text)
		#rate = 80.34
		#soms = number * rate
		#context.bot.send_message(chat_id=chat.id, text=str(soms) + " сом")
		chat = update.effective_chat
		context.bot.send_message(chat_id=chat.id, text='ЗАВЕРШЕНИЕ ПОИСКА !!!')
		
	except:
		context.bot.send_message(chat_id=chat.id, text="Введите ключевое слово для поиска статей")



updater = Updater(token, use_context=True)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", on_start))
dispatcher.add_handler(MessageHandler(Filters.all, on_message))

updater.start_polling()
updater.idle()

