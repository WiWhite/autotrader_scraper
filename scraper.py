import requests
from multiprocessing.pool import ThreadPool
import csv


def keywords(url):

    dealer = url.split('/')[6]
    dealer_id = url.split('/')[6].split('-')[-1]
    long_geo = url.split('/')[4]
    geo = url.split('/')[5]

    return dealer, dealer_id, long_geo, geo


def get_response(url):
    return requests.get(url).json()


def create_urls(keywords):
    list_urls = []

    dealer, dealer_id, long_geo, geo = keywords
    page = 1

    path = 'https://www.autotrader.co.uk/json/dealers/stock?advertising-' \
            'location=at_cars&advertising-location=at_profile_cars&dealer=' \
            '{1}&onesearchad=Used&onesearchad=Nearly%20New&page={4}&sort=price'\
            '-asc&fromDealerSearchResults=%2Fdealers%2F{2}%' \
            '2F{3}%2F{0}%2Fstock%3Fsort' \
            '%3Dprice-asc%26page%3D1%26dealer%3D9882%26onesearchad%' \
            '3DUsed%26onesearchad%3DNearly%2520New%26advertising-location%' \
            '3Dat_cars%26advertising-location%3Dat_profile_cars'

    url = path.format(dealer, dealer_id, long_geo, geo, page)
    response = get_response(url)
    count_car = response['stockResponse']['totalResults']
    list_urls.append(url)
    page += 1

    while round(count_car / 11) >= len(list_urls):
        url = path.format(
            dealer,
            dealer_id,
            long_geo,
            geo,
            page
        )

        list_urls.append(url)
        page += 1

    return list_urls


def create_data(urls):
    data = []
    actions = ThreadPool().imap_unordered(get_response, urls)
    for action in actions:
        data.append(action)
    return data


def preprocessing_data(data):

    title = []
    price = []
    colour = []
    condition = []
    doors = []
    seats = []
    year = []
    mileage = []
    volume = []
    transmission = []
    body = []
    fuel = []
    images = []

    count_cars = 0
    for page in data:
        count_cars += len(page['stockResponse']['results'])
        for car in page['stockResponse']['results']:
            try:
                title.append(car['titleAndSubtitle']['title'])
            except KeyError:
                title.append(None)
            try:
                price.append(car['price'])
            except KeyError:
                price.append(None)
            try:
                colour.append(car['vehicle']['colour'])
            except KeyError:
                colour.append(None)
            try:
                condition.append(car['vehicle']['condition'])
            except KeyError:
                condition.append(None)
            try:
                mileage.append(car['vehicle']['mileage'])
            except KeyError:
                mileage.append(None)
            try:
                year.append(car['vehicle']['yearText'])
            except KeyError:
                year.append(None)
            img = []
            try:
                for image in car['images']:
                    img.append(image['src'])
                images.append(img)
            except KeyError:
                images.append(None)
            description = car['description']
            try:
                split_description = description.split('|')
                doors.append(split_description[5])
            except KeyError:
                doors.append(None)
            try:
                split_description = description.split('|')
                seats.append(split_description[7])
            except:
                seats.append(split_description[6])
            transmission.append(split_description[4])
            body.append(split_description[1])
            fuel.append(split_description[5])
            volume.append(split_description[3])

    zip_object = zip(
        title,
        price,
        colour,
        condition,
        doors,
        seats,
        year,
        mileage,
        volume,
        transmission,
        body,
        fuel,
        images
    )

    return zip_object


def save_to_csv(zip_object, keywords):

    with open('{}.csv'.format(keywords[0]), 'w', encoding='utf-8') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow((
            'Title',
            'Price',
            'Colour',
            'Condition',
            'Doors',
            'Seats',
            'Year',
            'Mileage',
            'Volume',
            'Transmission',
            'Body',
            'Fuel',
            'Images'
        ))
        writer.writerows(zip_object)


def main(url):
    words = keywords(url)
    urls = create_urls(words)
    data = create_data(urls)
    save_to_csv(preprocessing_data(data), words)


if __name__ == '__main__':
    main()
