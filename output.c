#include <stdio.h>
#include <string.h>

#define ord( x ) ( ( int ) x )
#define chr( x ) ( ( char ) x )
#define inc( x ) ( x++ )
#define dec( x ) ( x-- )
#define insert( src, dest, index ) ( dest[ index - 1 ] = src )
#define length( str ) ( strlen( str ) )



int main( void )
{
	int i;
	int j;
	int n;
	
	scanf( "%d", &n );
	for( i = n; i >= 1; i += -1 ) 
	{
		for( j = ( n - i ); j >= 1; j += -1 ) 
		{
			printf( "%c", ' ' );
		}
		for( j = ( ( 2 * i ) - 1 ); j >= 1; j += -1 ) 
		{
			printf( "%c", '*' );
		}
		printf( "\n" );
	}
	return 0;
}
