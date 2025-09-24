# Booking.com web scraper
# -----
# scrapes data from every relevant property within a 2-mile radius of an input location
# input is address and checkin/checkout dates
# collects name, address, price, distance from input address, link, rating, number of rooms, and amenity list
# saves data in a sqlite3 database
# works as of 9/24/25


# import libraries
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import sqlite3
from word2number import w2n


# INPUT INFORMATION
location = "1400 Hubbell Pl, Seattle, WA 98101, USA"
checkin = "2025-09-20"
checkout = "2025-09-21"


# SCROLL FUNCTION
# scrolls to the bottom of the page to load more properties
def scroll(page, scroll_pause_time=2, max_scroll_attempts=10):

    # define variable for height of page
    previous_height = None

    # scroll until max scroll attempts has been reached
    for i in range(max_scroll_attempts):

        # scroll to bottom of current screen and wait for more to load
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(scroll_pause_time)

        # check if height changed - no change means scrolled to bottom of page
        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == previous_height:
            break

        # update page height variable
        previous_height = current_height


# SCRAPING FUNCTION
def scrape_booking(location: str, checkin: str, checkout: str, max_results=10):
    # testing urls
    #url = (
    #     f"https://www.booking.com/searchresults.html"
    #     f"?ss={location}"
    #     f"&label=gen173nr-1FCAEoggI46AdIM1gEaLQCiAEBmAExuAEHyAEM2AEB6AEB-AECiAIBqAIDuAKUo9vDBsACAdICJDVmMWZkMzBiLWU3N2QtNDUxYS1iMmU3LTU4YTc2OTUwZjYzONgCBeACAQ&sid=33469a4d9e60896eff638e1a36ece6f1&aid=304142"
    #     f"&lang=en-us&src=searchresults"
    #     f"&checkin={checkin}&checkout={checkout}"
    #     f"&group_adults=4&no_rooms=1&group_children=0"
    #     f"&nflt=distance%3D3220"
    # )

    #url = "https://www.booking.com/searchresults.html?ss=1400+Hubbell+Pl%2C+Seattle%2C+WA+98101%2C+USA&ssne=Seattle&ssne_untouched=Seattle&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaLQCiAEBmAExuAEHyAEM2AEB6AEB-AECiAIBqAIDuAKUo9vDBsACAdICJDVmMWZkMzBiLWU3N2QtNDUxYS1iMmU3LTU4YTc2OTUwZjYzONgCBeACAQ&sid=33469a4d9e60896eff638e1a36ece6f1&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=ChIJexvEfrVqkFQRLB2i_7xmQJw&dest_type=latlong&latitude=47.6121355&longitude=-122.32980540000001&ac_position=0&ac_click_type=g&ac_langcode=xu&ac_suggestion_list_length=2&search_selected=true&search_pageview_id=cec78226a9e39bb48ca57fd734e77823&ac_meta=KAIyAnh1WgdnZW9jb2Rl&checkin=2025-07-19&checkout=2025-07-20&group_adults=4&no_rooms=1&group_children=0"
    
    # url of booking website
    url = "https://www.booking.com"

    results = []
    

    with sync_playwright() as p:
        # uncomment below to clear out current table
        #delete_data = f"DELETE FROM {booking_data};"
        #cursor.execute(delete_data)
        #conn.commit()

        # launch chromium browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"Loading {url}")
        page.goto(url, timeout=60000)

        # locates search bar and searches for property based on input location
        page.locator("input[name='ss']").fill(location)

        # opens date selector and selects inputed checkin and checkout dates
        page.locator("button[data-testid='searchbox-dates-container']").click()
        page.locator(f"span[data-date='{checkin}']").click()
        page.locator(f"span[data-date='{checkout}']").click()

        # wait because sometimes the search misses a parameter if you click submit immediately
        time.sleep(0.5)

        # click submit button to search for input property
        page.locator("button[type='submit']").click()

        # wait for page to render
        time.sleep(2)

        # loop that scrolls to bottom of page and clicks load more buttons until all properties have been loaded
        # booking only loads 25 properties per page so this loop is necessary to load all the relevant properties
        while True:
            try:
                # scroll to bottom of current page
                scroll(page)
                
                # locate "load more" button to load more properties (if button exists)
                button = page.locator('button.de576f5064.b46cd7aad7.d0a01e3d83.dda427e6b5.bbf83acb81.a0ddd706cc')
                button.wait_for(state="visible", timeout=2000)

                # if button doesn't exist break the loop
                if not button.is_enabled():
                    break
                
                # click "load more" button
                button.click()

            except Exception as e:
                break
        
        # scroll one more time to make sure all properties are loaded
        scroll(page)

        # uncomment below to test if scroll function actually loaded all properties
        # input()


        # save content of page to local file
        content = page.content()
        with open("page.html", "w") as text_file:
            text_file.write(content)

        soup = BeautifulSoup(content, "html.parser")

        # find number of property listings that meet criteria
        # max results part broke the code idk why but it seems to work without it
        listings = soup.select("div[data-testid='property-card']")#[:max_results]
        print(f"number of listings found: {len(listings)}")

        # scrape desired data for each listing
        for listing in listings:
            name = listing.select_one("div[data-testid='title']").get_text(strip=True)
            price_el = listing.select("span[data-testid='price-and-discounted-price']")
            price = price_el[0].get_text(strip=True).replace("$", "") if price_el and len(price_el) > 0 else "N/A"
            total_cost = price_el[1].get_text(strip=True).replace("$", "") if price_el and len(price_el) > 1 else "N/A"
            location = listing.select_one("span[data-testid='address']").get_text(strip=True)
            distance = listing.select_one("span[data-testid='distance']").get_text(strip=True).removesuffix(" from your search address").removesuffix(" miles from map center")

            # append data to results dictionary
            results.append({
                "name": name,
                "price": price,
                "total_cost": total_cost,
                "location": location,
                "distance": distance,

            })

        # some data (rating, number of bedrooms, amenities) isn't available from thumbnails in initial search
        # instead go to each listing's booking page to collect rest of data
        for i, listing in enumerate(listings):
            
            # collect and go to listing link
            link = listing.select_one("a[data-testid='title-link']").get('href')
            #print(link)
            page.goto(link, timeout=60000)

            # collect listing rating
            rating = page.locator("div[aria-hidden='true']").nth(1).inner_text()

            # data on number of rooms embedded in huge paragraph
            # locate paragraph and turn into list
            rooms = page.locator("a[rel='main']").nth(0).inner_text()
            room_list = rooms.split()

            # the data on number of rooms is always formatted in one of two ways
            # search for string "-Bedroom" in list ("One-Bedroom", "Two-Bedroom", etc.)
            if any("-Bedroom" in item for item in room_list):
                
                # sometimes multiple similar rooms are listed (hotels usually) so we just take the first
                blank_bedrooms = [item for item in room_list if "-Bedroom" in item]
                number_rooms = str(blank_bedrooms[0])

                # remove "-Bedroom" suffix and use word to number to convert to numerals
                number_rooms = number_rooms.removesuffix("-Bedroom")
                number_rooms = w2n.word_to_num(number_rooms)
            
            # in rare cases there's a space between the number and word "Bedroom"
            # search for string "Bedroom"
            if "Bedroom" in room_list:

                # find the number of rooms based on the index of "Bedroom" string
                if room_list.index("Bedroom") >= 1:
                    number_rooms = room_list[room_list.index("Bedroom")-1]
                
                # convert number to numerals
                number_rooms = w2n.word_to_num(number_rooms)

            # if no specification on number of rooms is listed, it means there's only one room
            else:
                number_rooms = "1"

            # locate the list of amenities
            amenities = page.locator("div[data-testid='property-most-popular-facilities-wrapper']").locator('.f6b6d2a959').all()
            amenity_list = []

            # isolate the text from the html for each amenity found
            for amenity in amenities:
                amenity = amenity.inner_text()

                # check for dupes before adding to amenity list
                if amenity not in amenity_list:
                    amenity_list.append(amenity)
            
            # reformatting the list as a string with amentities seperated by a comma
            amenity_list_str = ""
            for i in amenity_list:
                amenity_list_str = amenity_list_str + i + ", "
            amenity_list_str = amenity_list_str.removesuffix(", ")
            #print(amenity_list_str)

            # update results with additional data
            results[i].update({
                "link": link,
                "rating": rating,
                "number_rooms": number_rooms,
                "amenities": amenity_list_str
            })

        # close chromium browser
        browser.close()

    # return results dictionary
    return results


# create sqlite connection
connection = sqlite3.connect('booking_database.db')
cursor = connection.cursor()


# uncomment below to create new table (table should already be created)
#create_table = """CREATE TABLE booking_data (
#name TEXT,
#location TEXT,
#price INTEGER);"""
#cursor.execute(create_table)
#location_input = "1400+Hubbell+Pl%2C+Seattle%2C+WA+98101%2C+USA"


# MAIN FUNCTION
if __name__ == "__main__":
    
    # runs scraping function
    results = scrape_booking(location, checkin, checkout)

    # add data for each property to sqlite database
    for i, result in enumerate(results, 1):

        # uncomment below for debugging
        #print(f"{i}. {result['name']}, {result['location']}, {result['price']}/{result['total_cost']}, {result['distance']}")
        
        # create variables for results
        name, location, price, distance = result['name'], result['location'], result['total_cost'], result['distance']
        link, rating, number_rooms, amenities = result['link'], result['rating'], result['number_rooms'], result['amenities']

        # UNCOMMENT BELOW TO ADD DATA TO SQLITE3 DATABASE
        sql_query = "INSERT INTO booking_data (name, location, price, distance, link, rating, number_of_rooms, amenities) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        cursor.execute(sql_query, (name, location, price, distance, link, rating, number_rooms, amenities))
        connection.commit()
    connection.close()
