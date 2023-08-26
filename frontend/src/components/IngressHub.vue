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

  // Function to determine the TLS status for an ingress
  function tlsStatus(ingress) {
      const rulesWithTLS = ingress.rules.filter(rule => rule.tls === "true").length;

      if (rulesWithTLS === ingress.rules.length) return 'Yes';
      if (rulesWithTLS > 0) return 'Partial';
      return 'No';
  }
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
                        <div class="card mb-4">
                            <div class="card-body">
                                <h4 class="card-title text-center">{{ ingress.name }}</h4>
                                <p class="card-text">
                                    <div class="row">
                                        <div class="col-6 text-left"><strong>Namespace:</strong></div>
                                        <div class="col-6 text-right">{{ ingress.namespace }}</div>
                                    </div>
                                    <div class="row">
                                        <div class="col-6 text-left"><strong>TLS:</strong></div>
                                        <div class="col-6 text-right">
                                            <span :class="{
                                                'badge': true,
                                                'bg-success': tlsStatus(ingress) === 'Yes',
                                                'bg-warning': tlsStatus(ingress) === 'Partial',
                                                'bg-danger': tlsStatus(ingress) === 'No'
                                            }">{{ tlsStatus(ingress) }}</span>
                                        </div>
                                    </div>
                                    <div v-if="ingress.rules.length === 1">
                                        <div class="d-flex align-items-center">
                                            <strong class="me-2">Host: </strong>
                                            <span :class="{
                                                'badge': true,
                                                'bg-success': ingress.rules[0].tls === 'true',
                                                'bg-danger': ingress.rules[0].tls === 'false',
                                                'me-2': true,
                                                'text-nowrap': true,
                                                'fixed-width-pill': true
                                            }">{{ ingress.rules[0].tls === 'true' ? 'HTTPS' : 'HTTP' }}</span>
                                            
                                            <span v-if="ingress.rules[0].paths.length === 1">
                                                <a :href="(ingress.rules[0].tls === 'true' ? 'https' : 'http') + '://' + ingress.rules[0].host + ingress.rules[0].paths[0]" target="_blank">
                                                    {{ ingress.rules[0].host + ingress.rules[0].paths[0] }}
                                                </a>
                                            </span>
                                            
                                            <div v-else class="d-flex align-items-center">
                                                <span>{{ ingress.rules[0].host }}</span>
                                                <a class="btn btn-link p-0 ml-2" :data-bs-toggle="'collapse'" :href="'#collapsePathsSingleRule' + index" role="button" aria-expanded="false">
                                                    Show paths
                                                </a>
                                            </div>
                                        </div>
                                    
                                        <div v-if="ingress.rules[0].paths.length > 1" :class="'collapse'" :id="'collapsePathsSingleRule' + index">
                                            <ul class="list-unstyled ml-4">
                                                <li v-for="path in ingress.rules[0].paths">
                                                    <a :href="(ingress.rules[0].tls === 'true' ? 'https' : 'http') + '://' + ingress.rules[0].host + path" target="_blank">
                                                        {{ path }}
                                                    </a>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    
                                    

                                    <div v-else>
                                        <div class="d-flex align-items-center">
                                            <strong>Hosts: </strong>
                                            <a class="btn btn-link p-0 ml-2" :data-bs-toggle="'collapse'" :href="'#collapseHosts' + index" role="button" aria-expanded="false">
                                                Show hosts
                                            </a>
                                        </div>
                                        <div :class="'collapse'" :id="'collapseHosts' + index">
                                            <ul class="list-unstyled">
                                                <li v-for="rule in ingress.rules">
                                                    <div class="d-flex align-items-center">
                                                        <span :class="{
                                                            'badge': true,
                                                            'bg-success': rule.tls === 'true',
                                                            'bg-danger': rule.tls === 'false',
                                                            'me-2': true,
                                                            'text-nowrap': true,
                                                            'fixed-width-pill': true
                                                        }">{{ rule.tls === 'true' ? 'HTTPS' : 'HTTP' }}</span>
                                    
                                                        <!-- Single path -->
                                                        <a v-if="rule.paths.length === 1" :href="(rule.tls === 'true' ? 'https' : 'http') + '://' + rule.host + rule.paths[0]" target="_blank">
                                                            {{ rule.host + rule.paths[0] }}
                                                        </a>
                                    
                                                        <!-- Multiple paths -->
                                                        <span v-else>
                                                            {{ rule.host }}
                                                        </span>
                                                    </div>
                                    
                                                    <ul v-if="rule.paths.length > 1" class="list-unstyled ml-4">
                                                        <li v-for="path in rule.paths">
                                                            <a :href="(rule.tls === 'true' ? 'https' : 'http') + '://' + rule.host + path" target="_blank">
                                                                {{ path }}
                                                            </a>
                                                        </li>
                                                    </ul>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    
                                    
                                    <div class="row align-items-end"> <!-- Added align-items-end here -->
                                        <div class="col-6 text-left"><strong>Cert-manager cluster issuer:</strong></div>
                                        <div class="col-6 text-right">{{ ingress.cert_manager_cluster_issuer || 'None' }}</div>
                                    </div>
                                </p>
                            </div>
                        </div>
                    </div>
                    <div v-if="ingressClass.ingresses.length === 0" class="col-md-12 text-muted">
                        No ingresses
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
  .fixed-width-pill {
      min-width: 55px; /* You can adjust this value to your preferred width */
      display: inline-block;
      text-align: center;
  }
</style>