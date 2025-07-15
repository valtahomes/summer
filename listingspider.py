import scrapy
import json

class listingspider(scrapy.Spider):
    name = 'listings'
    start_urls = ['https://www.booking.com/searchresults.html?ss=1400+Hubbell+Pl%2C+Seattl+...%3A+e%2C+WA+98101%2C+USA&ssne=1400+Hubbell+Pl%2C+Seattl+...%3A+e%2C+WA+98101%2C+USA&ssne_untouched=1400+Hubbell+Pl%2C+Seattl+...%3A+e%2C+WA+98101%2C+USA&efdco=1&label=gen173nr-1FCAQoggI49ANIM1gEaLQCiAEBmAExuAEHyAEM2AEB+...%3A+6AEB-AECiAIBqAIDuALxv4vDBsACAdICJGRhOGQ5YmQ2LTZmNGQtNDdiMC1iNTVhLTU2YjkxYzRmNz+...%3A+E5MdgCBeACAQ&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&latitude=47.6121355&longitude=-122.3298054&checkin=2025-07-04&checkout=2025-07-05&group_adults=4&no_rooms=1&group_children=0']


    
    def start_requests(self):
        payload = '''
            {"operationName":"FullSearch","variables":{"includeBundle":false,"input":{"acidCarouselContext":null,"childrenAges":[],"dates":{"checkin":"2025-07-04","checkout":"2025-07-05"},"doAvailabilityCheck":false,"encodedAutocompleteMeta":null,"enableCampaigns":true,"filters":{},"flexibleDatesConfig":{"broadDatesCalendar":{"checkinMonths":[],"los":[],"startWeekdays":[]},"dateFlexUseCase":"DATE_RANGE","dateRangeCalendar":{"checkin":["2025-07-04"],"checkout":["2025-07-05"]}},"forcedBlocks":null,"location":{"searchString":"1400 Hubbell Pl, Seattl ...: e, WA 98101, USA","destType":"LATLONG","latitude":47.6121355,"longitude":-122.3298054},"metaContext":{"metaCampaignId":0,"externalTotalPrice":null,"feedPrice":null,"hotelCenterAccountId":null,"rateRuleId":null,"dragongateTraceId":null,"pricingProductsTag":null},"nbRooms":1,"nbAdults":4,"nbChildren":0,"showAparthotelAsHotel":true,"needsRoomsMatch":false,"optionalFeatures":{"forceArpExperiments":true,"testProperties":false},"pagination":{"rowsPerPage":25,"offset":100},"rawQueryForSession":"/searchresults.html?label=gen173nr-1FCAQoggI49ANIM1gEaLQCiAEBmAExuAEHyAEM2AEB+...%3A+6AEB-AECiAIBqAIDuALxv4vDBsACAdICJGRhOGQ5YmQ2LTZmNGQtNDdiMC1iNTVhLTU2YjkxYzRmNz+...%3A+E5MdgCBeACAQ&aid=304142&ss=1400+Hubbell+Pl%2C+Seattl+...%3A+e%2C+WA+98101%2C+USA&ssne=1400+Hubbell+Pl%2C+Seattl+...%3A+e%2C+WA+98101%2C+USA&ssne_untouched=1400+Hubbell+Pl%2C+Seattl+...%3A+e%2C+WA+98101%2C+USA&efdco=1&lang=en-us&sb=1&src_elem=sb&src=searchresults&latitude=47.6121355&longitude=-122.3298054&checkin=2025-07-04&checkout=2025-07-05&group_adults=4&no_rooms=1&group_children=0","referrerBlock":{"blockName":"searchbox"},"sbCalendarOpen":true,"sorters":{"selectedSorter":null,"referenceGeoId":null,"tripTypeIntentId":null},"travelPurpose":2,"seoThemeIds":[],"useSearchParamsFromSession":true,"merchInput":{"testCampaignIds":[]},"webSearchContext":{"reason":"CLIENT_SIDE_UPDATE","source":"SEARCH_RESULTS","outcome":"SEARCH_RESULTS"},"clientSideRequestId":"a8c875f1591b07f7"},"carouselLowCodeExp":false},"extensions":{},"query":"query FullSearch($input: SearchQueryInput!, $carouselLowCodeExp: Boolean!, $includeBundle: Boolean = false) {\n  searchQueries {\n    search(input: $input) {\n      ...FullSearchFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment FullSearchFragment on SearchQueryOutput {\n  banners {\n    ...Banner\n    __typename\n  }\n  breadcrumbs {\n    ... on SearchResultsBreadcrumb {\n      ...SearchResultsBreadcrumb\n      __typename\n    }\n    ... on LandingPageBreadcrumb {\n      ...LandingPageBreadcrumb\n      __typename\n    }\n    __typename\n  }\n  carousels {\n    ...Carousel\n    __typename\n  }\n  destinationLocation {\n    ...DestinationLocation\n    __typename\n  }\n  entireHomesSearchEnabled\n  dateFlexibilityOptions {\n    enabled\n    __typename\n  }\n  flexibleDatesConfig {\n    broadDatesCalendar {\n      checkinMonths\n      los\n      startWeekdays\n      losType\n      __typename\n    }\n    dateFlexUseCase\n   

            } '''

            
        headers = {
            "Content-Type": "application/json"
        }

        yield scrapy.Request(
             url = self.start_urls[0],
             method="POST",
             body = payload,
             headers=headers,
             callback=self.parse,
             meta={"cursor", None}
        )



    def parse(self, response):
        """for products in response.css('div.aa97d6032f'):
                
                yield {
                    'name': products.css('div.b87c397a13.a3e0b4ffd1::text').get(),
                    'price': products.css('span.b87c397a13.ab607752a2::text').get(),
                    'link': products.css('a.bd77474a8e').attrib['href'],
                    }"""
        
        data = json.loads(response.text)
        items = data['data']['searchQueries']['search']['results']
        for item in items:
            node = item['displayName']
            yield {
                'name': node['text'],
            }
            
        

        



                
        
