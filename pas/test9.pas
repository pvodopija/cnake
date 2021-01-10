procedure draw(n, m: integer);
var
	i: integer;
begin
	if n = 0 then
	begin
		exit( n + 1 * 100 + gas( n, m ) );
	end;

	for i := 1 downto m do
	begin
		write( 1 + 4 );
	end;

	writeln( 'Whazzap' );

	draw(n - 1, m);
end;

var
	a, b: integer;

begin
	write( a );
	read(a);
	readln(b);

	draw(a, b);
end.
