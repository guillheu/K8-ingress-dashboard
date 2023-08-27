<script setup>
import { ref } from 'vue';
const ingresses = ref([]);

  // Initialize collapseStates with empty array, it will be populated later
  const collapseStates = ref([]);

  async function fetchIngresses() {
      const response = await fetch('/ingresses.json');
      const data = await response.json();
      ingresses.value = data;

      // Update collapseStates based on the newly fetched ingresses
      collapseStates.value = ingresses.value.map(() => true);
  }

  // Function to toggle the collapse state for a given index
  function toggleCollapse(index) {
      collapseStates.value[index] = !collapseStates.value[index];
  }

  // Fetch ingress data on component creation
  fetchIngresses();


  import IngressCard from './IngressCard.vue';


</script>

<template>

        <div id="app" class="container mt-4">
        <h1 class="mb-4 text-center">Ingresses</h1>
        <div v-for="(ingressClass, index) in ingresses" class="mb-4">
            <div class="d-flex align-items-center">
                <button class="btn btn-primary" type="button" data-bs-toggle="collapse" @click="toggleCollapse(index)" :data-bs-target="'#collapse' + index" aria-expanded="false">
                    {{ ingressClass.ingress_class_name }}
                    <span :class="collapseStates[index] ? 'bi bi-chevron-down' : 'bi bi-chevron-right'"></span>
                </button>
                <span class="ms-2">LB IP : {{ ingressClass.lb_ip }}</span>
            </div>

            <div :id="'collapse' + index" class="collapse show">
                <div class="row">
                    <div class="col-md-4" v-for="(ingress, index) in ingressClass.ingresses">


                      <IngressCard :ingress="ingress" />




                    </div>
                    <div v-if="ingressClass.ingresses.length === 0" class="col-md-12 text-muted">
                        No ingresses
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>