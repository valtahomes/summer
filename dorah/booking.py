from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import sqlite3

def scrape_booking(location: str, checkin: str, checkout: str, max_results=10):
    # url = (
    #     f"https://www.booking.com/searchresults.html"
    #     f"?ss={location}&checkin_year_month_monthday={checkin}"
    #     f"&checkout_year_month_monthday={checkout}"
    #     "&group_adults=2&no_rooms=1&group_children=0"
    # )

    url = (
         f"https://www.booking.com/searchresults.html"
         f"?ss={location}"
         f"&label=gen173nr-1FCAEoggI46AdIM1gEaLQCiAEBmAExuAEHyAEM2AEB6AEB-AECiAIBqAIDuAKUo9vDBsACAdICJDVmMWZkMzBiLWU3N2QtNDUxYS1iMmU3LTU4YTc2OTUwZjYzONgCBeACAQ&sid=33469a4d9e60896eff638e1a36ece6f1&aid=304142"
         f"&lang=en-us&src=searchresults"
         f"&checkin={checkin}&checkout={checkout}"
         f"&group_adults=4&no_rooms=1&group_children=0"
         f"&nflt=distance%3D3220"
     )

    #url = "https://www.booking.com/searchresults.html?ss=1400+Hubbell+Pl%2C+Seattle%2C+WA+98101%2C+USA&ssne=Seattle&ssne_untouched=Seattle&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaLQCiAEBmAExuAEHyAEM2AEB6AEB-AECiAIBqAIDuAKUo9vDBsACAdICJDVmMWZkMzBiLWU3N2QtNDUxYS1iMmU3LTU4YTc2OTUwZjYzONgCBeACAQ&sid=33469a4d9e60896eff638e1a36ece6f1&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=ChIJexvEfrVqkFQRLB2i_7xmQJw&dest_type=latlong&latitude=47.6121355&longitude=-122.32980540000001&ac_position=0&ac_click_type=g&ac_langcode=xu&ac_suggestion_list_length=2&search_selected=true&search_pageview_id=cec78226a9e39bb48ca57fd734e77823&ac_meta=KAIyAnh1WgdnZW9jb2Rl&checkin=2025-07-19&checkout=2025-07-20&group_adults=4&no_rooms=1&group_children=0"

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"Loading {url}")
        page.goto(url, timeout=60000)

        # time.sleep(2)  # wait for JS rendering
        # page.get_by_role("button", name="Search").click()
        # time.sleep(5)  # wait for JS rendering

        content = page.content()
        # save to local file
        with open("page.html", "w") as text_file:
            text_file.write(content)
        soup = BeautifulSoup(content, "html.parser")
        listings = soup.select("div[data-testid='property-card']")[:max_results]
        print(f"number of listings found: {len(listings)}")

        for listing in listings:
            name = listing.select_one("div[data-testid='title']").get_text(strip=True)
            price_el = listing.select("span[data-testid='price-and-discounted-price']")
            price = price_el[0].get_text(strip=True) if price_el and len(price_el) > 0 else "N/A"
            total_cost = price_el[1].get_text(strip=True) if price_el and len(price_el) > 1 else "N/A"
            location = listing.select_one("span[data-testid='address']").get_text(strip=True)
            distance = listing.select_one("span[data-testid='distance']").get_text(strip=True)
            results.append({
                "name": name,
                "price": price,
                "total_cost": total_cost,
                "location": location,
                "distance": distance
            })

        #input("")
        browser.close()

    return results

#location_input = "1400+Hubbell+Pl%2C+Seattle%2C+WA+98101%2C+USA"
location_input = "1400 Hubbell Pl, Seattle, WA 98101, USA"

connection = sqlite3.connect('booking_database.db')
cursor = connection.cursor()
#sql_command = """CREATE TABLE booking_data (
#name TEXT,
#location TEXT,
#price INTEGER);"""
#cursor.execute(sql_command)


# Example usage
if __name__ == "__main__":
    location = location_input.replace(" ", "+").replace(",", "2C")
    checkin = "2025-07-29"
    checkout = "2025-07-30"
    results = scrape_booking(location, checkin, checkout)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}, {result['location']}, {result['price']}/{result['total_cost']}, {result['distance']}")
        name, location, price, distance = result['name'], result['location'], result['price'], result['distance']


        #sql_query = "INSERT INTO booking_data (name, location, price) VALUES (?, ?, ?);"
        #cursor.execute(sql_query, (name, location, price))
        connection.commit()
    connection.close()
