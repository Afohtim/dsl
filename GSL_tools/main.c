#include "enriched_semantics.h"
#include <stdio.h>

main()
{
	vector_view_t vecview = vector_view_from_array(5, (double []) { 1, 1, 1, 1, 1 });	// view vecview = ` 1, 1, 1, 1, 1, 1 `.	-- initialize
	vector_t vec = VECTOR_INIT(vgp_clone(&vecview.vector), true);				// vector vec = vecview; 		-- or dereference *vecview?
	vector_t vec2 = vector_move_or_copy(&(vector_t ) VECTOR_DEFAULT, &vec);			// vector vec2 = vec; 			-- (smart copy) assignment
	vector_println(vec);									// vec;					-- send result of vector expression evaluation to the output
	vector_destroy(&vec);									// destroy vec;				-- ??? explicit destroy
	vector_println(vec);									// vec;
	vector_println(vec2);
	vector_println(vector_scale(vec2, 5.0));						// vec * 5;				-- scaling, 5 * vec is the same
	//vector_t vec3 = vector_move_or_copy(&(vector_t ) VECTOR_DEFAULT, &vec2);
	vector_t vec3 = vector_move_or_copy(&(vector_t ) VECTOR_DEFAULT, & (vector_t) VECTOR_INIT(vector_scale(vec2, 5.0).vgp, true));
	vector_println( vector_move_or_copy(&vec2,&vec) );					// vec2 = vec;

	scalar_result_t res = vector_ddot(vec3, vec3); 							// vec_a . vecb;
	printf("status=%d, result=%g\n", res.status, res.result);

	// vector_t _vec = vector_new(3, 2., 2., 2.);						// view = &` 2, 2, 2 `
	// TODO: vector_view_t view = &[3..5] vec2;
	// TODO: view_assign(view, _vec);							// *view = _vec;			-- vec2 = ` 5, 5, 2, 2, 2 `
	// 
	// max, min, sum, multiplication, subtraction, rev, +x, = x;
	// == , < -?
	// * -- matrix product


	vector_t vecp = vector_move_or_copy(&(vector_t ) {.vgp = NULL, .bound = false}, &vec);
}

