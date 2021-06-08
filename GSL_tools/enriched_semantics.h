#ifndef	ENRICHED_SEMANTICS_H
# define	ENRICHED_SEMANTICS_H

#include <stdbool.h>
#include <assert.h>

#include <gsl/gsl_vector.h>

/* v == NULL if invalid
 * invalid implies !bound
 */
struct _vector_wrapper {
	gsl_vector *vgp;
	bool bound;
};

typedef struct _vector_wrapper vector_t;

/* v.data == NULL if invalid (undef) */
typedef gsl_vector_view vector_view_t;

#define VECTOR_INIT(_vgp, _bound)	{ .vgp = _vgp, .bound = _bound }
#define VECTOR_INIT_VGP(_vgp)	{ .vgp = _vgp }
#define VECTOR_DEFAULT			VECTOR_INIT(NULL, false)
#define VIEW_DEFAULT			{ .vector.data = NULL }

struct _scalar_result {
	double	result;
	int	status;
};
typedef struct _scalar_result scalar_result_t;

#define SCALAR_RESULT(_result, _status) (scalar_result_t ) { .result = _result, .status = _status };

vector_t vector_new_from_list(int n, ...);

/*
static inline
vector_t vector_from_view(vector_view_t *vector_view)
{
	if (vector_view_is_invalid(vector_view))
		return (vector_t) { .vgp = NULL, .bound = false };

	
	return (vector_t ) { .vector = gsl_vector_alloc(vector_view), .bound = false };
}
*/

static inline
vector_view_t vector_view_from_array(size_t n, double *base)
{
	return gsl_vector_view_array(base, n);
}

//static inline
vector_t vector_copy_or_clone(vector_t *, gsl_vector *);

static inline
vector_t vector_copy_from_view(vector_t *vdstp, vector_view_t *viewsrcp) 
{
	return vector_copy_or_clone(vdstp, &viewsrcp->vector);
}

/*
static inline
vector_t vector_assign(vector_t *vwvar, vector_t vwexpr) 
{
	assert (vwvar->bound);
	if (vwvar->vgp == vwexpr->v)
		return *vwvar;

	if (! vector_is_undef(vwvar)) {
		if (vwvar->vgp->size == vwexpr->v->size) {
			if (! vector_is_bound(vwexpr)) {
				vector_move(vwvar, vwexpr);
			gsl_vector_memcpy(vwvar, vwexpr->vgp);
			vector_check_destroy(vwexpr);
			return
		if (vwvar->vgp->size != vwexpr->v->size) { // check block size?
			gls_vector_free(vwvar->vgp);
		}
	if (vector_is_undef(vwvar))
		*vwvar = vector_init(vwexpr);
	else if (vwvar->vgp->size != vwexpr->v->size) { // check block size?
	}
	else if (vwvar->vgp->size == vwexpr->v->size)
		gsl_vector_memcpy(vwvar, vwexpr->vgp); 
	return vector_init(vw
	if (vwvar->vgp == NULL
		       	|| vwvar->vgp !
*/

static inline
bool vector_is_valid(vector_t *vp)
{
	return vp->vgp != NULL;
}

static inline
bool vector_is_undef(vector_t *vp)
{
	return vp->vgp == NULL;
}

static inline
bool vector_is_bound(vector_t *vp)
{
	return vp->bound;
}

static inline
vector_t vector_bind(vector_t vp) 
{
	return (vector_t) { .vgp = vp.vgp, .bound = true };
}

static inline
vector_t vector_mark_bound(vector_t *vp) 
{
	vp->bound = true;
	return *vp;
}

static inline
vector_t vector_mark_unbound(vector_t *vp) 
{
	vp->bound = false;
	return *vp;
}


static inline
void vector_mark_bound_ifvalid(vector_t *vp) 
{
	vp->bound = vector_is_valid(vp);
}
 
static inline
void vector_unchecked_destroy(vector_t *vp)
{
	gsl_vector_free(vp->vgp);
	vp->vgp = NULL;
	vector_mark_unbound(vp);
}

static inline
void vector_free(vector_t *vp)
{
	if (vector_is_valid(vp))
		vector_unchecked_destroy(vp);
}

static inline
void vector_update(vector_t *vp)
{
	if (! vector_is_bound(vp))
		vector_free(vp);
}

static inline
bool vgp_is_view(gsl_vector *vgp)
{
	return vgp != NULL && vgp->owner == 0;
}

static inline
bool vgp_is_valid(gsl_vector *vgp)
{
	return vgp != NULL && vgp->data != NULL;
}

static inline
bool vector_view_is_valid(vector_view_t *vp)
{
	return vgp_is_valid(&vp->vector);
}

static inline
vector_view_t vector_view_from_vector(vector_t vec)
{
	vector_update(&vec);

	if (! vector_is_valid(&vec))
		return (vector_view_t ) VIEW_DEFAULT; // { .vector.data = NULL };

	return gsl_vector_subvector(vec.vgp, 0, vec.vgp->size);
}

static inline
gsl_vector *vgp_clone(gsl_vector *vgsrcp) 
{
	gsl_vector *vgdstp = gsl_vector_alloc(vgsrcp->size);
	gsl_vector_memcpy(vgdstp, vgsrcp);
	return vgdstp;
	//return (vector_t ) { .vgp = vgdstp, .bound = false };
}

vector_t vector_move_or_copy(vector_t *, vector_t *);

// binary ops
scalar_result_t vector_ddot(vector_t , vector_t );

// flags
static inline
void vector_destroy(vector_t *vp)
{
	if (vector_is_valid(vp))
		vector_unchecked_destroy(vp);
}

void vgp_print(gsl_vector *vgp);

static inline
void vector_print(vector_t v)
{
	vgp_print(v.vgp);
	vector_update(&v);
}

static inline
void vector_println(vector_t v)
{
	vector_print(v);
	putchar('\n');
}

// BLAS
vector_t vector_scale(vector_t , double );

#endif //	ENRICHED_SEMANTICS_H
