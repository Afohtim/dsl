int main (){
vector_view_t vector_view_0 = vector_view_from_array(3, (double []) { 3, 4, 5 }) ;
vector_t a = VECTOR_INIT(vgp_clone(&vector_view_0.vector), true) ;
vector_println(a) ;
vector_view_t vector_view_1 = vector_view_from_array(3, (double []) { 1, 4, 6 }) ;
vector_t b = VECTOR_INIT(vgp_clone(&vector_view_1.vector), true) ;
vector_println(b) ;
scalar_result_t scalar_expr = vector_ddot(a, b) ;
printf("status=%d, result=%g\n", res.status, res.result) ;
double res = scalar_res.res ;

}

