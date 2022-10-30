import json
import time
from Api import Api
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


def find_possible_room(empty_room, hotel, c):
    need_room = c["amount"]
    stay = c["check_out_date"] - c["check_in_date"]
    for idx, (now_floor, now_room) in enumerate(empty_room):
        # 해당 층이 예약 필요 방의 수를 수용 가능한지
        if now_room + need_room - 1 <= w:
            can_checkin = True
            for i_idx in range(now_room + 1, now_room + need_room):
                if hotel[now_floor][i_idx] > 0:
                    can_checkin = False
                    break
            # 숙박할 자리 있으면 숙박 시킨다
            if can_checkin:
                for i in range(need_room):
                    hotel[now_floor][now_room + i] = stay

                return now_floor, now_room, can_checkin

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


def main():
    fail_cnt = 0
    t = time.time()
    api_1 = Api("b11062ac496663726d930510fb365241", problem)

    # 호텔방 구현
    hotel = [[0 for _ in range(w + 1)] for p in range(h + 1)]

    visit = defaultdict(list)
    for day in range(1, s + 1):
        print("오늘", day)
        # 호텔방에 사람 있으면 남은 날짜 감소 / 그날 체크아웃하면 그방에 사람 입실 가능하므로 먼저 해줌
        for i in range(1, 1 + h):
            for j in range(1, 1 + w):
                if hotel[i][j] != 0:
                    hotel[i][j] -= 1
        # 체크인시키기
        hotel, real_check = check_in(hotel, visit, day)
        print("visit", visit[day])
        print("real", real_check)

        # 예약받기
        req = api_1.new_requests()
        # 예약 점수가 높은순으로 정렬한다
        req.sort(key=lambda x: sort_by_num_and_stay(x), reverse=True)

        replies = []
        print("이날진짜", hotel)
        for r in req:
            # 지금 부터 얘가 체크인 할 때 까지 시뮬 돌리기
            print(r)
            # 시뮬 돌릴 가짜 호텔 만듬
            fake_hotel = copy.deepcopy(hotel)
            print("계속호텔", hotel)
            print("fake", fake_hotel)
            for fake_day in range(day + 1, r["check_in_date"] + 1):
                for i in range(1, 1 + h):
                    for j in range(1, 1 + w):
                        if fake_hotel[i][j] != 0:
                            fake_hotel[i][j] -= 1
                # 하루 지날 때 마다 가짜 호텔 체크인 시킨다 / fake는 디버깅하기 위해서 사용
                fake_hotel, _ = check_in(fake_hotel, visit, fake_day)
                print("fake날짜지나고", fake_hotel, fake_day)
                # 가짜호텔 하루 지나게하기

            # 가능한 방 찾기
            reply = "refused"
            for i in range(1, h + 1):
                for idx in range(1, w + 1):
                    # 이 사람이 체크인 할 때 맨 앞부터 빈방 찾기
                    if fake_hotel[i][idx] == 0:
                        # 한 층에 모든 사람들 체크인 시켜야 하는데 필요한 방의 수가 한 층의 남은 방의 수를 넘지 않는지 확인
                        if idx + r["amount"] - 1 <= w:
                            # for문이 사람이 있어서 멈춘건지, 아니면 끝까지 다 돌았고 모두 비어있어서 멈춘건지 확인하기 위해
                            fflg = 0
                            # 방이 실제로 숙박 가능한지 확인하기
                            for i_idx in range(idx + 1, idx + r["amount"]):
                                # 방에 사람 있으면 바로 중지
                                if fake_hotel[i][i_idx] > 0:
                                    fflg = 1
                                    break
                            # 숙박 가능하다면
                            if fflg == 0:
                                reply = "accepted"
                                print("가짜체크인할떄 들어갈 수 있는 방", i, idx)

                        # 위 조건에 충족 못하면 어차피 그 뒤에 방들이 비어있어도 인원 수용못하니 다음 층으로 넘어가기
                        # 예 : 5개 방 필요한데 앞에서 부터 탐색한 비어있는 방부터 맨 마지막까지 3개방이 남으면 무시하고 넘어가기
                        break
                if reply == "accepted":
                    break

            # refused accepted
            tmp = {}
            tmp["id"] = r["id"]
            tmp["reply"] = reply
            replies.append(tmp)
            # 요청받고 방문자 리스트에 넣기 , 그래서 이번 예약 요청의 다음번 요청이 지금 받은 예약도 반영하도록
            if reply == "accepted":
                visit[r["check_in_date"]].append(r)

        print("reply", replies)
        print(day, api_1.reply(replies))
        cnt = api_1.simulate(real_check)
        fail_cnt += cnt
        print("fail", cnt)

        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

    print(api_1.score())
    print(fail_cnt)
    print(time.time() - t)


if __name__ == "__main__":
    main()
