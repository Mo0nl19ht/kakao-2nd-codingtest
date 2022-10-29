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


def check_in(hotel, visit, day, fake=0):
    if day == 12 and fake == 0:
        print(12)
    check = visit[day]
    check.sort(key=lambda x: sort_by_num_and_stay(x), reverse=True)
    if fake == 1:
        print("가짜 체크인", check, day)
    real_check = []

    for c in check:

        posible_room = []
        for i in range(1, h + 1):
            for idx in range(1, w + 1):
                if hotel[i][idx] == 0:
                    posible_room.append((i, idx))
        if day == 12 and fake == 0 and c["id"] == 348018:
            print(1)
        amount = c["amount"]
        stay = c["check_out_date"] - c["check_in_date"]
        floor = 0
        room = 0
        flg = -1
        for idx, (f, r) in enumerate(posible_room):
            # 해당 층에 체크인 가능하면
            if r + amount - 1 <= w:
                fflg = 0
                for i_idx in range(r + 1, r + amount):
                    if hotel[f][i_idx] > 0:
                        fflg = 1
                        break
                if fflg == 0:
                    for i in range(amount):
                        hotel[f][r + i] = stay
                    flg = idx
                    room = r
                    floor = f
                    break

        if flg != -1:
            tmp = {}
            tmp["id"] = c["id"]
            tmp["room_number"] = make_room_number(floor, room)

            real_check.append(tmp)

    return hotel, real_check


def main():
    fail_cnt = 0
    t = time.time()
    api_1 = Api("b11062ac496663726d930510fb365241", problem)

    hotel = [[0 for _ in range(w + 1)] for p in range(h + 1)]
    visit = defaultdict(list)
    for day in range(1, s + 1):
        print("오늘", day)
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

        req.sort(key=lambda x: sort_by_num_and_stay(x), reverse=True)

        replies = []
        print("이날진짜", hotel)
        for r in req:
            # 지금부터 얘가 체크인할떄까지 시뮬 돌리기
            print(r)
            fake_hotel = copy.deepcopy(hotel)
            print("계속호텔", hotel)
            print("fake", fake_hotel)
            for fake_day in range(day + 1, r["check_in_date"] + 1):
                for i in range(1, 1 + h):
                    for j in range(1, 1 + w):
                        if fake_hotel[i][j] != 0:
                            fake_hotel[i][j] -= 1
                fake_hotel, _ = check_in(fake_hotel, visit, fake_day, 1)
                print("fake날짜지나고", fake_hotel, fake_day)
                # 가짜호텔 하루 지나게하기

            # 가능한 방 찾기
            reply = "refused"
            for i in range(1, h + 1):
                for idx in range(1, w + 1):
                    if fake_hotel[i][idx] == 0:
                        if idx + r["amount"] - 1 <= w:
                            fflg = 0
                            for i_idx in range(idx + 1, idx + r["amount"]):
                                if fake_hotel[i][i_idx] > 0:
                                    fflg = 1
                                    break
                            if fflg == 0:
                                reply = "accepted"
                                print("가짜체크인할떄 들어갈 수 있는 방", i, idx)
                        break
                if reply == "accepted":
                    break

            # refused accepted
            tmp = {}
            tmp["id"] = r["id"]
            tmp["reply"] = reply
            replies.append(tmp)
            # 요청받고 방문자 리스트에 넣기
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
