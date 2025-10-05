steps(29).
time(0).
time(1).
time(2).
time(3).
time(4).
time(5).
time(6).
time(7).
time(8).
time(9).
time(10).
time(11).
time(12).
time(13).
time(14).
time(15).
time(16).
time(17).
time(18).
time(19).
time(20).
time(21).
time(22).
time(23).
time(24).
time(25).
time(26).
time(27).
time(28).
time(29).
disk(1).
disk(2).
disk(3).
disk(4).
disk(5).
disk(6).
disk(7).
disk(8).
disk(9).
disk(10).
disk(11).
disk(13).
disk(14).
disk(15).
disk(16).
disk(17).
disk(18).
disk(19).
disk(20).
disk(21).
on0(5,1).
on0(6,5).
on0(7,6).
on0(8,7).
on0(9,8).
on0(10,9).
on0(13,10).
on0(14,13).
on0(15,14).
on0(11,2).
on0(16,3).
on0(17,16).
on0(18,17).
on0(19,18).
on0(20,19).
on0(21,20).
on0(12,4).
ongoal(5,1).
ongoal(6,5).
ongoal(7,6).
ongoal(11,2).
ongoal(12,11).
ongoal(13,12).
ongoal(14,13).
ongoal(15,14).
ongoal(16,15).
ongoal(17,16).
ongoal(18,17).
ongoal(19,18).
ongoal(20,19).
ongoal(21,20).
ongoal(8,3).
ongoal(9,4).
ongoal(10,9).

on(0,N1,N) :- on0(N,N1).
onG(K,N1,N) :- ongoal(N,N1), steps(K).
:- time(T), on(T,N1,N), N1>=N.

move(T,N) | noMove(T,N) :- disk(N), time(T), steps(K), T<K.
:- move(T,N1), move(T,N2), N1!=N2.
:- time(T), steps(K), T<K, not diskMoved(T).
diskMoved(T) :- move(T,Fv1).

where(T,N) | noWhere(T,N) :- disk(N), time(T), steps(K), T<K.
:- where(T,N1), where(T,N2), N1!=N2.
:- disk(N), time(T), steps(K), T<K, not diskWhere(T).
diskWhere(T) :- where(T,Fv1).
:- move(T,N), N<5.

:-on(T,N,N1), move(T,N).

:-on(T,N,N1), where(T,N).

:-move(T,N), move(TM1,N), TM1=T-1.

on(TP1,N1,N) :- move(T,N), where(T,N1), TP1=T+1.

on(TP1,N,N1) :- time(T), steps(K), T<K,on(T,N,N1), not move(T,N1), TP1=T+1.

:- not on(K,N,N1), onG(K,N,N1), steps(K).
:- on(K,N,N1), not onG(K,N,N1),steps(K).

put(T,M,N) :- move(T,N), where(T,M), steps(K), T<K.



#project put(13,15,18).
#project put(11,20,21).
#project put(24,20,21).
#show put/3.
