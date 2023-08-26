-- CreateTable
CREATE TABLE "api_keys" (
    "key" VARCHAR NOT NULL,
    "expiration_date" BIGINT,
    "user_id" INTEGER,
    "name" VARCHAR,
    "created" BIGINT,

    CONSTRAINT "api_keys_pkey" PRIMARY KEY ("key")
);

-- CreateTable
CREATE TABLE "blacklist" (
    "token" VARCHAR(200) NOT NULL,

    CONSTRAINT "blacklist_pkey" PRIMARY KEY ("token")
);

-- CreateTable
CREATE TABLE "users" (
    "id" SERIAL NOT NULL,
    "identifier" VARCHAR,
    "email" VARCHAR,
    "hashed_pw" VARCHAR,
    "provider" VARCHAR,
    "image" VARCHAR,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_identities" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "provider" TEXT NOT NULL,
    "provider_id" TEXT NOT NULL,
    "provider_data" JSONB NOT NULL,

    CONSTRAINT "user_identities_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "credit_purchase" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "credit_amount" INTEGER NOT NULL,
    "created_date" BIGINT,
    "payment_method" VARCHAR,
    "payment_details" JSONB,

    CONSTRAINT "credit_purchase_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "credit_tracking" (
    "user_id" INTEGER NOT NULL,
    "credit" INTEGER NOT NULL,

    CONSTRAINT "credit_tracking_pkey" PRIMARY KEY ("user_id")
);

-- CreateIndex
CREATE INDEX "ix_users_id" ON "users"("id");

-- AddForeignKey
ALTER TABLE "api_keys" ADD CONSTRAINT "api_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "user_identities" ADD CONSTRAINT "user_identities_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "credit_purchase" ADD CONSTRAINT "credit_purchase_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "credit_tracking" ADD CONSTRAINT "credit_tracking_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE NO ACTION;
