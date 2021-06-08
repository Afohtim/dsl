#include "enriched_semantics.h"
#include <stdarg.h>
#include <stdio.h>
#include <assert.h>

#include <gsl/gsl_blas.h>

static inline
bool vector_try_move(vector_t *vdstp, vector_t *vsrcp) 
{
	if (! vector_is_bound(vsrcp)) {
		vector_free(vdstp);
		vdstp->vgp = vsrcp->vgp;
		vdstp->bound = vector_is_valid(vdstp);
		vector_mark_bound_ifvalid(vdstp);
		return true;
	}
	return false;
}

//static inline
vector_t vector_new_from_list(int n, ...)
{
	va_list ap;
	vector_t v;

	va_start(ap, n);
	v.vgp = gsl_vector_alloc(n);
	for (int i; i < n; i++)
		gsl_vector_set(v.vgp, i, va_arg(ap, double));
	va_end(ap);
	v.bound = true;

	return v;
}

//void vector_print(vector_t v)
void vgp_print(gsl_vector *vgp)
{
	if (! vgp || ! vgp_is_valid(vgp))
		printf("%s`undef`", vgp_is_view(vgp) ? "&" : "");

	else {
		printf("`"); // "\\");

		int i;
		for (i = 0; i < vgp->size - 1; i++)
			printf("%g, ", gsl_vector_get(vgp, i));

		if (i == vgp->size - 1)
			printf("%g", gsl_vector_get(vgp, i));
		printf("`"); // \\");
	}
}

//void vector_print(vector_t v)

vector_t vector_copy_or_clone(vector_t *vdstp, gsl_vector *vgsrcp)
{
	if (! vector_is_valid(vdstp))
		*vdstp = (vector_t ) VECTOR_INIT_VGP(vgp_clone(vgsrcp));

	else if (vdstp->vgp->size == vgsrcp->size)
		gsl_vector_memcpy(vdstp->vgp, vgsrcp); 

	else {
		vector_free(vdstp);
		*vdstp = (vector_t ) VECTOR_INIT_VGP(vgp_clone(vgsrcp));
	}
	
	vector_mark_bound(vdstp);
	return *vdstp;
}

vector_t vector_move_or_copy(vector_t *vdstp, vector_t *vsrcp) 
{
	if (vdstp->vgp == vsrcp->vgp)
		return *vdstp;

	if (vector_try_move(vdstp, vsrcp))
		vector_mark_bound(vdstp);
	else
		vector_copy_or_clone(vdstp, vsrcp->vgp);

	return *vdstp;
}

vector_t vector_scale(vector_t vp, double factor)
{
	if (! vector_is_valid(&vp))
		return vp;

	gsl_vector *outvgp = vector_is_bound(&vp) ? vgp_clone(vp.vgp) : vp.vgp;
	gsl_vector_scale(outvgp, factor);

	return (vector_t ) VECTOR_INIT(outvgp, false);
}

scalar_result_t vector_ddot(vector_t vec_a, vector_t vec_b)
{
	if (! vector_is_valid(&vec_a) || ! vector_is_valid(&vec_b)) // vec_a.vgp->size == vec_b.vgp->size )
		return SCALAR_RESULT(0.0/0.0, false);	// -> 0/0.0;

	double result;
	int status = gsl_blas_ddot(vec_a.vgp, vec_b.vgp, &result);

	if (vec_a.vgp != vec_b.vgp)
		vector_update(&vec_a);
	vector_update(&vec_b);

	return SCALAR_RESULT(result, status);
}

// outtakes
static inline
bool vector_try_copy(vector_t *vdstp, gsl_vector *viewsrcp) 
{
	assert(viewsrcp != NULL);

	if (vector_is_valid(vdstp) && vdstp->vgp->size == viewsrcp->size) {
		gsl_vector_memcpy(vdstp->vgp, viewsrcp); 
		return true;
	}
	return false;
}

/*
static inline
vector_t vector_move_or_clone(vector_t vw) 
{
	if (! vw.bound) {
		vw.bound = true; // || vw.vgp;
		return vw;
	}
	else if (vector_is_undef(&vw))
		return vw;
	else {
		gsl_vector *dst = gsl_vector_alloc(vw.vgp->size);
		gsl_vector_memcpy(dst, vw.vgp); 
	}
	return vw;
}
*/

