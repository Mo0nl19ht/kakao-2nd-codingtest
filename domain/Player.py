from Api import Api
from Hotel import Hotel


class Player:
    def __init__(self, code, problem, h, w, total_day):
        self.code = code
        self.problem = problem
        self.total_day = total_day
        self.api = Api(code, problem)
        self.hotel = Hotel(h, w)

    def start(self):
        for day in range(1, self.total_day + 1):
            # 호텔방에 사람 있으면 남은 날짜 감소 / 그날 체크아웃하면 그방에 사람 입실 가능하므로 먼저 해줌
            self.hotel.check_out()
            real_check = self.hotel.check_in(day)
            # 예약받기
            reservation_list = self.api.new_requests()
            # 예약 점수가 높은순으로 정렬한다
            reservation_list.sort(
                key=lambda x: self.hotel.sort_by_num_and_stay(x), reverse=True
            )
            # 예약 받을지 정하는 로직
            replies = self.hotel.make_replies(day, reservation_list)
            # 예약 요청 보내기
            self.api.reply(replies)
            # 체크인 시키기
            self.api.simulate(real_check)

        return self.api.score()
