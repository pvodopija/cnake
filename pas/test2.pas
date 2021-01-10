function jeProst(n: integer): boolean;
	var
		i: integer;
	
	begin
		if n = 5 then
		begin
			exit( ( 7 = n ) = true )
		end;
		
		exit( true );
		write( 'AFTER EXIT' );
	end;

var
	n, i, s: integer;
	b: boolean;

begin
	readln(n);

	i := 0;
	s := 1;
	b := false;

	repeat
		b := jeProst( s );
		writeln( ' ', b );
		
		s := s + 1;
	until s = n;

	writeln(s);
end.
