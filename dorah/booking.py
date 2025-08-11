from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import sqlite3
from word2number import w2n


# scrolls to the bottom of the page to load more properties
def scroll(page, scroll_pause_time=2, max_scroll_attempts=10):

    previous_height = None
    for i in range(max_scroll_attempts):

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(scroll_pause_time)

        current_height = page.evaluate("document.body.scrollHeight")
        if current_height == previous_height:
            break
        previous_height = current_height



def scrape_booking(location: str, checkin: str, checkout: str, max_results=10):
    # url = (
    #     f"https://www.booking.com/searchresults.html"
    #     f"?ss={location}&checkin_year_month_monthday={checkin}"
    #     f"&checkout_year_month_monthday={checkout}"
    #     "&group_adults=2&no_rooms=1&group_children=0"
    # )

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
    
    url = "https://www.booking.com"

    results = []
    

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"Loading {url}")
        page.goto(url, timeout=60000)


        page.locator("input[name='ss']").fill(location)
        page.locator("button[data-testid='searchbox-dates-container']").click()

        #checkin and checkout dates
        page.locator(f"span[data-date='{checkin}']").click()
        page.locator(f"span[data-date='{checkout}']").click()

        time.sleep(0.5)
        page.locator("button[type='submit']").click()

        
        time.sleep(2)  # wait for JS rendering
        # page.get_by_role("button", name="Search").click()
        # time.sleep(5)  # wait for JS rendering

        
        # SCROLL TO BOTTOM OF PAGE
        #properties_found = page.locator("h1[aria-live='assertive']").text_content().removesuffix(" properties found")
        #properties_found = properties_found[(properties_found.find(":")+2):]
        #scroll_total = (int(properties_found)+25-1) // 25

        while True:
            try:
                scroll(page)
                
                button = page.locator('button.de576f5064.b46cd7aad7.d0a01e3d83.dda427e6b5.bbf83acb81.a0ddd706cc')
                button.wait_for(state="visible", timeout=2000)
                if not button.is_enabled():
                    break
                
                button.click()

            except Exception as e:
                break
        
        scroll(page)

        input()
        #LOAD PAGE
        content = page.content()
        # save to local file
        with open("page.html", "w") as text_file:
            text_file.write(content)
        soup = BeautifulSoup(content, "html.parser")
        #page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        #time.sleep(5)

        listings = soup.select("div[data-testid='property-card']")#[:max_results]
        print(f"number of listings found: {len(listings)}")
        #input("")

        #SCRAPES DATA
        for listing in listings:
            name = listing.select_one("div[data-testid='title']").get_text(strip=True)
            price_el = listing.select("span[data-testid='price-and-discounted-price']")
            price = price_el[0].get_text(strip=True).replace("$", "") if price_el and len(price_el) > 0 else "N/A"
            total_cost = price_el[1].get_text(strip=True).replace("$", "") if price_el and len(price_el) > 1 else "N/A"
            location = listing.select_one("span[data-testid='address']").get_text(strip=True)
            distance = listing.select_one("span[data-testid='distance']").get_text(strip=True).removesuffix(" from your search address").removesuffix(" miles from map center")

            results.append({
                "name": name,
                "price": price,
                "total_cost": total_cost,
                "location": location,
                "distance": distance,

            })

        for idx, listing in enumerate(listings):

            #page.locator('title-link').click()
            #page.locator('button.de576f5064.b46cd7aad7.d0a01e3d83.dda427e6b5.bbf83acb81.a0ddd706cc').click
            
            link = listing.select_one("a[data-testid='title-link']").get('href')
            print(link)
            page.goto(link, timeout=60000)


            rating = page.locator("div[aria-hidden='true']").nth(1).inner_text()

            rooms = page.locator("a[rel='main']").nth(0).inner_text()
            room_list = rooms.split()
            if any("-Bedroom" in item for item in room_list):
                blank_bedrooms = [item for item in room_list if "-Bedroom" in item]
                number_rooms = str(blank_bedrooms[0])
                number_rooms = number_rooms.removesuffix("-Bedroom")
                number_rooms = w2n.word_to_num(number_rooms)
            if "Bedroom" in room_list:
                if room_list.index("Bedroom") >= 1:
                    number_rooms = room_list[room_list.index("Bedroom")-1]
                number_rooms = w2n.word_to_num(number_rooms)

            else:
                number_rooms = "1"

            amenities = page.locator("div[data-testid='property-most-popular-facilities-wrapper']").locator('.f6b6d2a959').all()
            amenity_list = []
            #input()
            for amenity in amenities:
                amenity = amenity.inner_text()
                if amenity not in amenity_list:
                    amenity_list.append(amenity)
            amenity_list_str = ""
            for i in amenity_list:
                amenity_list_str = amenity_list_str + i + ", "
            amenity_list_str = amenity_list_str.removesuffix(", ")
            print(amenity_list_str)

            results[idx].update({
                "link": link,
                "rating": rating,
                "number_rooms": number_rooms,
                "amenities": amenity_list_str
            })

        #input("")
        browser.close()

    return results



connection = sqlite3.connect('booking_database.db')
cursor = connection.cursor()
#sql_command = """CREATE TABLE booking_data (
#name TEXT,
#location TEXT,
#price INTEGER);"""
#cursor.execute(sql_command)
#location_input = "1400+Hubbell+Pl%2C+Seattle%2C+WA+98101%2C+USA"


#INPUT INFORMATION
location = "1400 Hubbell Pl, Seattle, WA 98101, USA"
checkin = "2025-08-12"
checkout = "2025-08-13"


if __name__ == "__main__":
    #location = location_input.replace(" ", "+").replace(",", "2C")
    
    results = scrape_booking(location, checkin, checkout)
    for i, result in enumerate(results, 1):
        #print(f"{i}. {result['name']}, {result['location']}, {result['price']}/{result['total_cost']}, {result['distance']}")
        name, location, price, distance = result['name'], result['location'], result['total_cost'], result['distance']

        link, rating, number_rooms, amenities = result['link'], result['rating'], result['number_rooms'], result['amenities']


        # UNCOMMENT BELOW TO ADD TO SQLITE3 DATABASE
        sql_query = "INSERT INTO booking_data (name, location, price, distance, link, rating, number_of_rooms, amenities) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        cursor.execute(sql_query, (name, location, price, distance, link, rating, number_rooms, amenities))
        connection.commit()
    connection.close()
