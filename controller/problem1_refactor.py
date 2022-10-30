import time
from domain.Api import Api
from collections import defaultdict
import copy

h = 3
w = 20
s = 200
problem = 1


def sort_by_num_and_stay(x):
    return x["amount"] * (x["check_out_date"] - x["check_in_date"])


def make_room_number(floor, room):
    room_number = str(floor)

    if room < 10:
        return room_number + "00" + str(room)
    elif room < 100:
        return room_number + "0" + str(room)
    else:
        return room_number + str(room)


def find_empty_room(hotel):
    empty_room = []
    for i in range(1, h + 1):
        for idx in range(1, w + 1):
            if hotel[i][idx] == 0:
                empty_room.append((i, idx))

    return empty_room


def make_request(id, floor, room):
    request = {}
    request["id"] = id
    request["room_number"] = make_room_number(floor, room)

    return request


def check_out(hotel):
    for i in range(1, 1 + h):
        for j in range(1, 1 + w):
            if hotel[i][j] != 0:
                hotel[i][j] -= 1


def make_reply_request(id, reply):
    reply_request = {}
    reply_request["id"] = id
    reply_request["reply"] = reply
    return reply_request


def find_possible_room(empty_room, hotel, c, fake=False):
    need_room = c["amount"]
    stay = c["check_out_date"] - c["check_in_date"]
    for idx, (now_floor, now_room) in enumerate(empty_room):
        # 해당 층이 예약 필요 방의 수를 수용 가능한지
        if now_room + need_room - 1 <= w:
            can_checkin = True
            # 방들이 모두 비었는지 확인
            for i_idx in range(now_room + 1, now_room + need_room):
                if hotel[now_floor][i_idx] > 0:
                    can_checkin = False
                    break
            # 숙박할 자리 있으면 숙박 시킨다
            if can_checkin:
                if fake:
                    return "accepted"
                for i in range(need_room):
                    hotel[now_floor][now_room + i] = stay

                return now_floor, now_room, can_checkin
    if fake:
        return "refused"
    return -1, -1, False


def check_in(hotel, visit, day):
    check = visit[day]
    # 점수를 많이 받기 위해서 받을 점수가 높은 순으로 정렬함
    check.sort(key=lambda x: sort_by_num_and_stay(x), reverse=True)
    real_check = []
    for c in check:
        empty_room = find_empty_room(hotel)
        floor, room, can_checkin = find_possible_room(empty_room, hotel, c)
        if can_checkin:
            real_check.append(make_request(c["id"], floor, room))

    return hotel, real_check


def make_replies(day, hotel, requests, visit):
    replies = []
    for r in requests:
        # 지금 부터 얘가 체크인 할 때 까지 시뮬 돌리기
        fake_hotel = copy.deepcopy(hotel)
        for fake_day in range(day + 1, r["check_in_date"] + 1):
            check_out(fake_hotel)
            # 하루 지날 때 마다 가짜 호텔 체크인 시킨다
            fake_hotel, _ = check_in(fake_hotel, visit, fake_day)

        # 가능한 방 찾기
        empty_room = find_empty_room(fake_hotel)
        reply = find_possible_room(empty_room, fake_hotel, r, True)
        replies.append(make_reply_request(r["id"], reply))

        # 요청받고 방문자 리스트에 넣기 , 그래서 이번 예약 요청의 다음번 요청이 지금 받은 예약도 반영하도록
        if reply == "accepted":
            visit[r["check_in_date"]].append(r)
    return replies


def main():
    fail_cnt = 0
    t = time.time()
    api_1 = Api("b11062ac496663726d930510fb365241", problem)

    # 호텔방 구현
    hotel = [[0 for _ in range(w + 1)] for p in range(h + 1)]

    visit = defaultdict(list)
    for day in range(1, s + 1):
        # 호텔방에 사람 있으면 남은 날짜 감소 / 그날 체크아웃하면 그방에 사람 입실 가능하므로 먼저 해줌
        check_out(hotel)
        # 체크인시키기
        hotel, real_check = check_in(hotel, visit, day)
        # 예약받기
        requests = api_1.new_requests()
        # 예약 점수가 높은순으로 정렬한다
        requests.sort(key=lambda x: sort_by_num_and_stay(x), reverse=True)
        replies = make_replies(day, hotel, requests, visit)
        # 예약 요청 보내기
        api_1.reply(replies)
        # 체크인 시키기
        fail_cnt += api_1.simulate(real_check)

    print(api_1.score())
    print(fail_cnt)
    print(time.time() - t)


if __name__ == "__main__":
    main()
