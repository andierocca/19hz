import requests
import csv
import datetime
from tokens import access_tokens
import re
import urllib2

start = "start_time"
end = "end_time"
name = "name"
place = "place"
promoter = "owner"
ticket_link = "ticket_uri"
#maybe add later for parsing price and age limit
#description = "description"

Fields = [name, place, promoter, ticket_link]

def main():
	f = open('events.csv', 'wb')
	writer = csv.writer(f)
	writer.writerow(['Day', 'Name', '?', 'Place', 'Time', 'Price', 'Age', 'Promoter', 'Ticket Link', 'Facebook Link', 'Date'])
	event_list = get_event_list()
	for event_ids in event_list:
		for event_id in event_ids:
			print event_id
			try:
				event_data = format_event(event_id[7:-1])
				if event_data != None:
					writer.writerow(event_data)
			except:
				print 'error'
				writer.writerow(['ERROR', ("https://www.facebook.com/events/" + event_id[7:-1])])

	f.close()

"""
returns list of lists of event id portion of urls formatted like 'events/.../'
"""
def get_event_list():
	txt_page = urllib2.urlopen("http://19hz.info/ATL/").read()
	txt_files = re.findall("<a href=\".+.txt\">", txt_page)
	all_events = list()
	for t in txt_files:
		try:
			fb_page = urllib2.urlopen("http://19hz.info/ATL/" + t[9:-2].replace('amp;', '')).read()
		except:
			print sys.exc_info()[0]
		event_ids = re.findall("events/[0-9]+/", fb_page)
		all_events.append(event_ids)
	return all_events


def format_event(event_id):
	json = get_json(event_id)

	values = list()

	start_str = get_field(json, start)
	start_date = format_datetime(start_str, True, "%a: %b %d")

	#if date is before today don't enter
	if start_date == None:
		return None

	for f in Fields:
		values.append(get_field(json, f))

	end_str = get_field(json, end)

	values.insert(0, start_date)
	#would hold ?
	values.insert(2, "")
	values.insert(4, format_datetime(start_str, False, "%I:%M%p") + "-" + format_datetime(end_str, False, "%I:%M%p"))
	#would hold price
	values.insert(5, "")
	#would hold age
	values.insert(6, "")
	values.insert(9, "https://www.facebook.com/events/" + event_id)
	values.insert(10, format_datetime(start_str, True, "%m/%d/%y"))

	return values

"""
Takes in dt_str - raw datetime string and converts it to a datetime object
Then formats datetime object according to the pattern and if a date is requested or a time
"""
def format_datetime(dt_str, is_date, pattern):
	if dt_str == "":
		return "?"

	#convert to datetime object
	dt = datetime.datetime.strptime(dt_str[:-5], "%Y-%m-%dT%H:%M:%S")
	#don't format past events
	if dt < datetime.datetime.now():
		return None
	if is_date:
		return dt.date().strftime(pattern)
	else:
		return dt.time().strftime(pattern)


def get_field(json, field):
	if field is promoter or field is ticket_link:
		json = get_json(json["id"], field)

	if field in json:
		if (field is place or field is promoter) and type(json[field]) is dict:
			try:
				return json[field][name]
			except:
				try:
					return json[field][location][street]
				except:
					return ""
		else:
			return json[field]
	else:
		return ""

def get_json(event_id, field = ""):
	t = access_tokens()
	field_add_on = "" if field == "" else ("fields=" + field + "&")
	query = "https://graph.facebook.com/%s?%saccess_token=%s|%s" % (event_id, field_add_on, t.app_id, t.app_secret)
	return requests.get(query).json()

main()