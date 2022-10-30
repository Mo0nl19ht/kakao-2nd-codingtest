import copy
from collections import defaultdict


class Hotel:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.hotel = [[0 for _ in range(w + 1)] for p in range(h + 1)]
        self.visit = defaultdict(list)

    def sort_by_num_and_stay(self, x):
        return x["amount"] * (x["check_out_date"] - x["check_in_date"])

    def _make_room_number(self, floor, room):
        room_number = str(floor)

        if room < 10:
            return room_number + "00" + str(room)
        elif room < 100:
            return room_number + "0" + str(room)
        else:
            return room_number + str(room)

    def _find_empty_room(self, hotel):
        empty_room = []
        for i in range(1, self.h + 1):
            for idx in range(1, self.w + 1):
                if hotel[i][idx] == 0:
                    empty_room.append((i, idx))

        return empty_room

    def _make_request(self, id, floor, room):
        request = {"id": id, "room_number": self._make_room_number(floor, room)}
        return request

    def _make_reply_request(self, id, reply):
        reply_request = {"id": id, "reply": reply}
        return reply_request

    def _select_hotel(self, fake_hotel):
        if fake_hotel:
            return fake_hotel
        else:
            return self.hotel

    def check_out(self, fake_hotel=None):
        hotel = self._select_hotel(fake_hotel)
        for i in range(1, 1 + self.h):
            for j in range(1, 1 + self.w):
                if hotel[i][j] != 0:
                    hotel[i][j] -= 1

    def find_possible_room(self, empty_room, c, fake=False):
        need_room = c["amount"]
        stay = c["check_out_date"] - c["check_in_date"]
        for idx, (now_floor, now_room) in enumerate(empty_room):
            # 해당 층이 예약 필요 방의 수를 수용 가능한지
            if now_room + need_room - 1 <= self.w:
                can_checkin = True
                # 방들이 모두 비었는지 확인
                for i_idx in range(now_room + 1, now_room + need_room):
                    if self.hotel[now_floor][i_idx] > 0:
                        can_checkin = False
                        break
                # 숙박할 자리 있으면 숙박 시킨다
                if can_checkin:
                    if fake:
                        return "accepted"
                    for i in range(need_room):
                        self.hotel[now_floor][now_room + i] = stay

                    return now_floor, now_room, can_checkin

        if fake:
            return "refused"
        return -1, -1, False

    def check_in(self, day, fake_hotel=None):
        hotel = self._select_hotel(fake_hotel)
        check_in_list = self.visit[day]
        # 점수를 많이 받기 위해서 받을 점수가 높은 순으로 정렬함
        check_in_list.sort(key=lambda x: self.sort_by_num_and_stay(x), reverse=True)
        real_check_in = []

        for check_in in check_in_list:
            empty_room = self._find_empty_room(hotel)
            floor, room, can_checkin = self.find_possible_room(empty_room, check_in)
            if can_checkin:
                real_check_in.append(self._make_request(check_in["id"], floor, room))

        return real_check_in

    def make_replies(self, day, reservation_list):
        replies = []
        for reservation in reservation_list:
            # 체크인 할 때 까지 시뮬 돌리기
            fake_hotel = copy.deepcopy(self.hotel)
            for fake_day in range(day + 1, reservation["check_in_date"] + 1):
                self.check_out(fake_hotel)
                # 하루 지날 때 마다 가짜 호텔 체크인 시킨다
                _ = self.check_in(fake_day, fake_hotel)

            # 가능한 방 찾기
            empty_room = self._find_empty_room(fake_hotel)
            reply = self.find_possible_room(empty_room, fake_hotel, reservation, True)
            replies.append(self.make_reply_request(reservation["id"], reply))

            # 요청받고 방문자 리스트에 넣기 , 그래서 이번 예약 요청의 다음번 요청이 지금 받은 예약도 반영하도록
            if reply == "accepted":
                self.visit[reservation["check_in_date"]].append(reservation)
        return replies
