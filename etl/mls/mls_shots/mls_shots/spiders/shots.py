import scrapy
from mls_shots.items import GameShotsItem

game_id = 0

class ShotSpider(scrapy.Spider):
    name="shots"
    allowed_domains = ["matchcenter.mlssoccer.com"]
    start_urls = ["http://www.mlssoccer.com/schedule?month=3&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=4&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=5&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=6&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=7&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=8&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=9&year=2014&club=select&club_options=9",
                  "http://www.mlssoccer.com/schedule?month=10&year=2014&club=select&club_options=9"]

    def parse(self, response):
        global game_id
        links =  [l + "/stats" for l in response.xpath('//div[@class="field-item even"]//@href').extract() if 'matchcenter' in l]
        for l in links:
            yield scrapy.http.Request(l, meta={'game_id': game_id}, callback=self.parse_game)
            game_id += 1


    def parse_game(self, response):
        home, away = response.xpath('//div[@class="sb-club-name"]/span[@class="sb-club-name-short"]/text()').extract()
        game = GameShotsItem()
        shots = [s for s in response.xpath('//svg[@class="sa-shot-box"]/g//@data-reactid').extract()]
        for s in shots:
            print s
            try:
                x1 = float(response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/line[@class="sa-shot-border"]//@x1'.format(s=s)).extract()[0].replace("%", ""))
                x2 = float(response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/line[@class="sa-shot-border"]//@x2'.format(s=s)).extract()[0].replace("%", ""))
                y1 = float(response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/line[@class="sa-shot-border"]//@y1'.format(s=s)).extract()[0].replace("%", ""))
                y2 = float(response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/line[@class="sa-shot-border"]//@x1'.format(s=s)).extract()[0].replace("%", ""))
                team = None
                if len(response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/line//@class'.format(s=s)).extract()) > 0:
                    shot_type = response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/line//@class'.format(s=s)).extract()[1]
                    if 'home' in shot_type:
                        team = home
                    elif 'away' in shot_type:
                        team = away
                    else:
                        team = '???'
                    try:
                        goal = response.xpath('//svg[@class="sa-shot-box"]/g[@data-reactid="{s}"]/circle//@class'.format(s=s)).extract()[0]
                    except IndexError:
                        goal = 'None'
                        
                    if "sa-shot-blocked" in shot_type:
                        outcome = 'blocked'
                    elif goal == "None":
                        outcome = 'off target'
                    elif "on-target" in goal:
                        outcome = 'on target'
                    elif "goal" in goal:
                        outcome = 'goal'
                    else:
                        outcome = '????'
                    
                    g_id = response.meta['game_id']
                    game["x1"] = x1
                    game["x2"] = x2
                    game["y1"] = y1
                    game["y2"] = y2
                    game["outcome"] = outcome
                    game["team"] = team
                    game["shot_id"] = s.split("$")[-1]
                    game["game_id"] = g_id

                
            except IndexError:
                pass
            yield game
