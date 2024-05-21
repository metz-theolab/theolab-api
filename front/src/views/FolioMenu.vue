<template>
    <BContainer>
        <!-- The current route is accessible as $route in the template -->
        You are viewing the folios of tradition {{ tradition }} and manuscript {{ manuscript }}.

        <BRow>
            <BButton @click="modal = !modal" variant="outline-primary" pill> Add a new folio</BButton>
            <BModal v-model="modal" title="Add new folio" @ok="createFolio()">

                <BForm @submit="createFolio">
                    <BFormGroup id="input-group-1" label="Folio name:" label-for="input-1">
                        <BFormInput id="input-1" v-model="newfolioname" placeholder="Enter folio name" required />
                    </BFormGroup>
                    <BFormGroup id="input-group-1" label="Folio position:" label-for="input-1">
                        <BFormSpinbutton id="demo-sb" v-model="newfolioposition" min="1" max="100" />
                    </BFormGroup>
                    <BFormGroup id="input-group-1" label="Folio image:" label-for="input-1">
                        <BFormFile class="mt-3" autofocus v-model="newfolioimage" />
                    </BFormGroup>
                </BForm>
            </BModal>
        </BRow>
        <BRow>

            <BCard class="m-2" v-for:="folio in folios" :key="folio.name" :title="folio.name"
                :img-src="getImageUrl(folio.image_url)" img-alt="Image" img-top tag="article" style="max-width: 15rem;">
                <BCardText>
                    Folio {{ folio.name }}
                </BCardText>

                <router-link :to="{ path: '/tradition/' + tradition + '/' + manuscript + '/' + folio.name }">
                    <BButton variant="primary" class="m-2">Explore</BButton>
                </router-link>
                <BButton variant="primary" @click="deleteFolio(folio)">Delete</BButton>
            </BCard>
        </BRow>
    </BContainer>
</template>

<script>

export default {
    name: 'ManuscriptMenu',
    data() {
        return {
            modal: false,
            folios: null,
            newfolioname: '',
            newfolioimage: null,
            newfolioposition: 0,
            tradition: this.$route.params.tradition,
            manuscript: this.$route.params.manuscript,
        }
    },
    methods: {
        getImageUrl(image) {
            return 'http://localhost:8000/static/' + image;
        },
        createFolio() {
            let formData = new FormData();
            if (this.newfolioimage != null)
                formData.append('image', this.newfolioimage);
            formData.append('position_in_manuscript', this.newfolioposition);
            console.log(formData)
            this.axios
                .post('/' + this.tradition + '/' + this.manuscript + '/' + this.newfolioname,
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    }
                )
                .then(response => console.log("Successfully created folio"));
            //window.location.reload();
        },
        deleteFolio(folio) {
            this.axios
                .delete('/' + this.tradition + '/' + this.manuscript + '/' + folio.name + '/')
                .then(response => console.log("Successfully deleted folio"));
            window.location.reload();
        }
    },
    mounted() {
        this.axios
            .get('/traditions/' + this.tradition + '/' + this.manuscript)
            .then(response => (this.folios = response.data));
    }
}
</script>