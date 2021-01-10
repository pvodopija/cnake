var
    niz : array[1..100] of integer;
    i, j, n, temp: integer;

begin
    readln(n);

    for i := 1 to n do
    begin
        read(niz[i]);
    end;

    for i := 1 to n do
    begin
        write(niz[i], ' ');
    end;

end.